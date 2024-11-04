import time
from abc import ABC, abstractmethod

import serial


class InputHandlerBase(ABC):
    @abstractmethod
    def read_input(self) -> str:
        pass


class StdinInputHandler(InputHandlerBase):
    def read_input(self) -> str:
        return input("enter input: ")


class ArduinoInputHandler(InputHandlerBase):
    def __init__(self, arduino: serial.Serial):
        self.arduino = arduino

    def read_input(self) -> str:
        return self.arduino.readline().decode("utf-8").strip()


class ArduinoOutputHandler:
    def __init__(self, arduino: serial.Serial):
        self.arduino = arduino

    def _send(self, output: str):
        self.arduino.write(output.encode())


class ArduinoScoreHandler(ArduinoOutputHandler):
    def send_score(self, score: int):
        assert 99999 >= score >= 0
        score_str = f"{score:05d}\n"
        print(f"sending score: {score_str}")
        self._send(f"{score:05d}\n")


class ArduinoClockHandler(InputHandlerBase, ArduinoOutputHandler):
    def __init__(self, arduino: serial.Serial):
        self.arduino = arduino
        self.time_offset = -1

    def set_time_offset(self, arduino_time: int):
        current_ms = time.time() * 1000
        self.time_offset = current_ms - arduino_time

    def send_countdown_time(self, server_time: int):
        arduino_time = server_time - self.time_offset
        print(f"Sending countdown time: {arduino_time}")
        self._send(f"{arduino_time}")

    def read_input(self) -> str:
        return self.arduino.readline().decode("utf-8").strip()
