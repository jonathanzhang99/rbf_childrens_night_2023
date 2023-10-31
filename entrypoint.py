import time
from typing import Literal
import serial
import serial.tools.list_ports
import threading
import pygame.mixer

from dataclasses import dataclass
from flask import Flask, render_template
from flask_socketio import SocketIO  # type: ignore
from datetime import datetime


BAUDRATE = 115200
PORT = "/dev/cu.usbmodem21401"

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)
arduino = serial.Serial(port=PORT, baudrate=BAUDRATE, timeout=1)
pygame.mixer.init()


@dataclass
class GameState:
    start_time: datetime
    game_length: int
    current_countdown: int = 5
    game_active: bool = False
    game_mode: Literal["Showdown", "Versus"] = "Showdown"
    score: int = 0

    def reset_game(self) -> None:
        self.game_active = False
        self.current_countdown = 5

    def start_game(self, game_length: int) -> None:
        self.start_time = datetime.now()
        self.game_length = game_length
        self.game_active = True
        self.score = 0

    def is_active(self) -> bool:
        return (
            self.game_active
            and (datetime.now() - self.start_time).total_seconds() < self.game_length
        )

    def countdown(self, countdown_sound: pygame.mixer.Sound) -> None:
        time_elapsed = (datetime.now() - self.start_time).total_seconds()
        time_remaining = self.game_length - time_elapsed
        if time_remaining <= self.current_countdown:
            self.current_countdown -= 1
            countdown_sound.play()


gs = GameState(datetime.now(), 0)


@app.route("/")
def index():
    # Render the template with the session ID
    return render_template("home.html", starting_score=gs.score, game_mode=gs.game_mode)


def arduino_listener():
    background_game_music = pygame.mixer.Sound("audio/draw_screen_loop.ogg")
    game_start = pygame.mixer.Sound("audio/game_start.ogg")
    game_won = pygame.mixer.Sound("audio/game_won.ogg")
    hit = pygame.mixer.Sound("audio/hit.ogg")
    countdown = pygame.mixer.Sound("audio/countdown.ogg")

    gs.reset_game()

    while True:
        value = arduino.readline().decode("utf-8").strip()
        value_arr = value.split()
        if gs.is_active():
            gs.countdown(countdown)

        if value:
            print(f"{datetime.now()}: {value}")
            if value_arr[0] == "EMIT":
                instruction = value_arr[1]
                if instruction == "SCORE":
                    score1 = int(value_arr[2])
                    score2 = int(value_arr[3])
                    socketio.emit("scoreUpdate", {"score1": score1, "score2": score2})

                elif instruction == "GAME_ACTIVE":
                    game_length = int(value_arr[2])
                    gs.start_game((game_length / 1000) + 1)

                    game_start.play()
                    time.sleep(1)
                    background_game_music.play(loops=-1)

                    print(f"starting game with ms: {game_length}")
                    socketio.emit("startGame", {"gameMs": game_length})

                elif instruction == "GAME_INACTIVE":
                    gs.reset_game()
                    print(f"ending game")
                    socketio.emit("endGame")
                    background_game_music.stop()
                    game_won.play()

                elif instruction == "TARGET_HIT":
                    hit.play()
                    target = int(value_arr[2])

                elif instruction == "GAME_MODE":
                    game_mode = int(value_arr[2])
                    gs.game_mode = "Versus" if game_mode else "Showdown"
                    socketio.emit("gameMode", {"gameMode": gs.game_mode})


update_thread = threading.Thread(target=arduino_listener)
update_thread.start()


if __name__ == "__main__":
    # Note: We use socketio.run here instead of app.run
    socketio.run(app)
