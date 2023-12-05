# RBG Children's Night 2023 Game

This repository contains the code that runs the webserver component of the Children's Night shooting game. It is reasonable for serving a simple templated HTML page that shows player a simple game interface and responds with audio cues to game events.

It is built using a Flask backend with Socketio for an event drive framework. Communication with the Arduino uses a super simple protocol through the Serial port.

## Installation
Supported python version: `^3.11`
Install [poetry](https://python-poetry.org/) and install deps in repo.
```
poetry
```

## Local Dev
Make sure that your Arduino is connected and update the `PORT` variable in `entrypoint.py` .
The frontend uses svelte packaged with bun.js.

TODO: Use environment variables/CLI input to set the PORT.
```
poetry run python entrypoint.py
```
in a different shell:
```
cd frontend
bun install
bun run dev
```