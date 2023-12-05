from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Literal
from flask_socketio import SocketIO  # type: ignore
import pygame.mixer


F = Callable[["GameState", List[str]], Dict[str, str | int | float]]


@dataclass
class GameState:
    socketio: SocketIO
    start_time: datetime = datetime.now()
    game_length_secs: int = 30
    current_countdown: int = 5
    game_active: bool = False
    game_mode: Literal["Showdown", "Versus"] = "Showdown"
    score: int = 0
    listeners: Dict[str, F] = field(default_factory=dict)

    def reset_game(self) -> None:
        self.game_active = False
        self.current_countdown = 5

    def start_game(self, game_length: int) -> None:
        self.start_time = datetime.now()
        self.game_length_secs = game_length
        self.game_active = True
        self.score = 0

    def is_active(self) -> bool:
        return (
            self.game_active
            and (datetime.now() - self.start_time).total_seconds()
            < self.game_length_secs
        )

    def countdown(self, countdown_sound: pygame.mixer.Sound) -> None:
        time_elapsed = (datetime.now() - self.start_time).total_seconds()
        time_remaining = self.game_length_secs - time_elapsed
        if time_remaining <= self.current_countdown:
            self.current_countdown -= 1
            countdown_sound.play()

    def register_listener(self, signal: str) -> Callable[[F], F]:
        def wrapper(f: F) -> F:
            self.listeners[signal] = f
            return f

        return wrapper

    def consume_signal(self, signal: str, data: List[str]) -> None:
        handler = self.listeners.get(signal)
        if not handler:
            return
        result = handler(self, data)
        self.socketio.emit(signal, result)
