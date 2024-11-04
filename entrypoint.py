import argparse
import threading
import time
from typing import List

import pygame.mixer
import serial
import serial.tools.list_ports
from flask import Flask, render_template
from flask_cors import CORS
from flask_socketio import SocketIO  # type: ignore

from game_state import GameState
from input_handler import (
    ArduinoClockHandler,
    ArduinoInputHandler,
    ArduinoScoreHandler,
    InputHandlerBase,
    StdinInputHandler,
)

parser = argparse.ArgumentParser(description="Game configuration")
parser.add_argument(
    "--test", action="store_true", default=False, help="Run in test mode"
)
parser.add_argument(
    "--debug", action="store_true", default=False, help="Enable debug mode"
)
parser.add_argument(
    "--baudrate-read",
    type=int,
    default=115200,
    help="Baud rate for reading from Arduino",
)
parser.add_argument(
    "--port-read",
    type=str,
    default="/dev/cu.usbmodem21301",
    help="Serial port for reading from Arduino",
)
parser.add_argument(
    "--baudrate-write", type=int, default=9600, help="Baud rate for writing to Arduino"
)
parser.add_argument(
    "--port-write",
    type=str,
    default=None,
    help="Serial port for writing to Arduino",
)
parser.add_argument(
    "--port-clock",
    type=str,
    default=None,
    help="Serial port for writing to Arduino",
)
parser.add_argument(
    "--baudrate-clock",
    type=int,
    default=9600,
    help="Baud rate for writing to Arduino",
)
parser.add_argument("--game-len", type=int, default=30, help="Game length in seconds")

args = parser.parse_args()

TEST = args.test
DEBUG = args.debug
BAUDRATE_READ = args.baudrate_read
PORT_READ = args.port_read
BAUDRATE_WRITE = args.baudrate_write
PORT_WRITE = args.port_write
GAME_LEN = args.game_len
PORT_CLOCK = args.port_clock
BAUDRATE_CLOCK = args.baudrate_clock

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
outputHandler: ArduinoScoreHandler | None = None
clockHandler: ArduinoClockHandler | None = None
arduino_clock: serial.Serial | None = None
arduino_write = serial.Serial(PORT_WRITE, BAUDRATE_WRITE)

if BAUDRATE_WRITE and PORT_WRITE:
    outputHandler = ArduinoScoreHandler(arduino_write)


if TEST:
    inputHandler = StdinInputHandler()
else:
    arduino_read = serial.Serial(PORT_READ, BAUDRATE_READ)
    inputHandler = ArduinoInputHandler(arduino_read)

if PORT_CLOCK and BAUDRATE_CLOCK:
    arduino_clock = serial.Serial(PORT_CLOCK, BAUDRATE_CLOCK)
    clockHandler = ArduinoClockHandler(arduino_clock)


@game.register_listener("SCORE")
def update_score(gs: GameState, data: List[str]) -> dict:
    score = int(data[0])

    if outputHandler:
        outputHandler.send_score(score)
    if len(data) == 1:
        return {"score1": score}
    elif len(data) == 2:
        return {"score1": int(data[0]), "score2": int(data[1])}

    raise Exception("Invalid score data")


@game.register_listener("GAME_ACTIVE")
def activate_game(gs: GameState, data: List[str]) -> dict:
    game_length = int(data[0])
    gs.start_game(game_length // 1000)
    if outputHandler:
        outputHandler.send_score(0)
    if clockHandler:
        clockHandler.send_countdown_time(int((gs.end_time.timestamp() + 2) * 1000))

    game_start.play()
    time.sleep(1)
    background_game_music.play(loops=-1)

    # logger.info(f"starting game with ms: {game_length}")
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
    print(f"Target hit: {target}")
    return {}


@game.register_listener("GAME_MODE")
def change_game_mode(gs: GameState, data: List[str]) -> dict:
    game_mode = int(data[0])
    hit.play()
    gs.game_mode = "Versus" if game_mode else "Showdown"
    print(gs.report())
    return {"gameMode": game_mode}


@game.register_listener("TIME_SYNC")
def sync_time(gs: GameState, data: List[str]):
    time_ms = int(data[0])
    print(f"Syncing time to {time_ms}")
    assert arduino_clock
    if clockHandler:
        clockHandler.set_time_offset(time_ms)
    return {}


@app.route("/")
def index():
    return render_template(
        "home.html", starting_score=game.score, game_mode=game.game_mode
    )


def listener(inputHandler: InputHandlerBase):
    print("Starting Server")
    game.reset_game()

    while True:
        value = inputHandler.read_input()

        if DEBUG:
            print(f"Read: {value}")
        value_arr = value.split()
        if game.is_active():
            game.countdown(countdown)

        if value:
            if value_arr[0] == "EMIT" and len(value_arr) > 1:
                _, signal, *data = value_arr
                game.consume_signal(signal, data)


def clock_listener(clockHandler: ArduinoClockHandler):
    while True:
        clock_value = clockHandler.read_input()
        if DEBUG:
            print(f"Clock Read: {clock_value}")

        if clock_value:
            clock_value_arr = clock_value.split()
            if clock_value_arr[0] == "EMIT" and len(clock_value_arr) > 1:
                _, signal, *data = clock_value_arr
                game.consume_signal(signal, data)


if __name__ == "__main__":
    # Note: We use socketio.run here instead of app.run
    update_thread = threading.Thread(target=listener, args=(inputHandler,))
    update_thread.start()

    if clockHandler:
        clock_thread = threading.Thread(target=clock_listener, args=(clockHandler,))
        clock_thread.start()

    socketio.run(app, port=5000)
