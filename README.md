# RBF Children's Night Game

The included spaghetti code in this repository powers the Brawl Stars shooting game for RBF Children's Night. The directory is roughly structured as follows:

`arduino/`: Contains the `.ino` file to be flashed to an Arduino device (tested only on Uno)

`entrypoint.py`, `game_state`, `input_handler`: The python files to run the threaded server. Includes a flask webserver using socket io to communicate with a frontend. Uses an event driven architecture to interact with the Arduinos.

`frontend/`: The frontend code for the game. Built with svelte using bun.js (not node!!). Note: Used only during 2021 and superceded by arduino ode

`audio/`: Brawl Stars audio sound effects

## Installation

Supported python version: `^3.12`

1. Install [poetry](https://python-poetry.org/)
2. run `poetry install`

## Local Dev

Make sure that your Arduino is connected.

### 2024 update:

`entrypoint.py` supports 3 arduino modules using the given options:

1. `port-read` + `baudrate-read`: Configures the arduino that drives the main game loop.
2. `port-write` + `baudrate-write`: Configures the arduino that drives the score.
3. `port-clock` + `baudrate-clock`: Configures the arduino that drives the countdown clock.

To run the server use:

```
poetry run python entrypoint.py --port-read /dev/<PORT> --baudrate-read <BAUDRATE> --port-write /dev/<PORT> --baudrate-write <BAUDRATE> --port-clock /dev/<PORT> --baudrate-clock <BAUDRATE>
```

### 2023 Usage:

The frontend uses svelte packaged with bun.js. This has not been updated or used for 2024 and can be run with:

```
cd frontend
bun install
bun run dev
```
