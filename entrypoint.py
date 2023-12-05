import time
from typing import List, Literal
import serial
import serial.tools.list_ports
import threading
import pygame.mixer

from flask import Flask, render_template
from flask_socketio import SocketIO  # type: ignore
from flask_cors import CORS
from datetime import datetime

from game_state import GameState
from input_handler import ArduinoInputHandler, InputHandlerBase, StdinInputHandler


TEST = True
BAUDRATE = 115200
PORT = "/dev/cu.usbmodem11401"
GAME_LEN = 30


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

pygame.mixer.init()
background_game_music = pygame.mixer.Sound("audio/draw_screen_loop.ogg")
game_start = pygame.mixer.Sound("audio/game_start.ogg")
game_won = pygame.mixer.Sound("audio/game_won.ogg")
hit = pygame.mixer.Sound("audio/hit.ogg")
countdown = pygame.mixer.Sound("audio/countdown.ogg")


game = GameState(socketio)

inputHandler: InputHandlerBase
if TEST:
    inputHandler = StdinInputHandler()
else:
    arduino = serial.Serial(PORT, BAUDRATE)
    inputHandler = ArduinoInputHandler(arduino)


@game.register_listener("SCORE")
def update_score(gs: GameState, data: List[str]) -> dict:
    if len(data) == 1:
        return {"score1": int(data[0])}
    elif len(data) == 2:
        return {"score1": int(data[0]), "score2": int(data[1])}

    raise Exception("Invalid score data")


@game.register_listener("GAME_ACTIVE")
def activate_game(gs: GameState, data: List[str]) -> dict:
    game_length = int(data[0])
    gs.start_game(game_length // 1000)

    game_start.play()
    time.sleep(1)
    background_game_music.play(loops=-1)

    # print(f"starting game with ms: {game_length}")
    return {"gameMs": game_length}


@game.register_listener("GAME_INACTIVE")
def end_game(gs: GameState, data: List[str]) -> dict:
    gs.reset_game()
    background_game_music.stop()
    game_won.play()
    return {}


@game.register_listener("TARGET_HIT")
def target_hit(gs: GameState, data: List[str]) -> dict:
    hit.play()
    target = int(data[0])
    return {}


@game.register_listener("GAME_MODE")
def change_game_mode(gs: GameState, data: List[str]) -> dict:
    game_mode = int(data[0])
    gs.game_mode = "Versus" if game_mode else "Showdown"
    return {"gameMode": gs.game_mode}


@app.route("/")
def index():
    return render_template(
        "home.html", starting_score=game.score, game_mode=game.game_mode
    )


def listener(inputHandler: InputHandlerBase):
    game.reset_game()

    while True:
        value = inputHandler.read_input()
        value_arr = value.split()
        if game.is_active():
            game.countdown(countdown)

        if value:
            print(f"{datetime.now()}: {value}")
            if value_arr[0] == "EMIT":
                _, signal, *data = value_arr
                game.consume_signal(signal, data)


update_thread = threading.Thread(target=listener, args=(inputHandler,))
update_thread.start()


if __name__ == "__main__":
    # Note: We use socketio.run here instead of app.run
    socketio.run(app, port=5000)
