import serial
from abc import ABC, abstractmethod


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
