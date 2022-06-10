import time
import random
from serial import Serial  # type: ignore
from typing import List, Dict, Literal
from abc import ABC, abstractmethod
from gigapixel.drivers.illumination import Illumination


BAUDRATE = 115200
N_LEDS = 16

Color = Literal['r', 'g', 'b']


class Illumination(ABC):
    @abstractmethod
    def __init__(self, port: str):
        pass

    @abstractmethod
    def turn_on_led(self, row: int, column: int, color: str, time: int = 0):
        pass

    @abstractmethod
    def turn_off_leds(self):
        pass

class AnilloDriver(Illumination):
    def __init__(self, port: str):
        self._port = port
        self._baudrate = BAUDRATE
        self._serial = self._open_serial()
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_off_leds()
        self._serial.close()

    def __del__(self):
        self.turn_off_leds()


