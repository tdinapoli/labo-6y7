from time import sleep
import time
import random
from serial import Serial  # type: ignore
from typing import List, Dict, Literal
from abc import ABC, abstractmethod


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
        #self._serial.write(int(1).to_bytes(1, byteorder="little", signed=False))
        print(self._serial)
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_off_leds()
        self._serial.close()

    def __del__(self):
        self.turn_off_leds()

    def _open_serial(self) -> Serial:
        """ Opens a serial port between Arduino and Python """

        serial = Serial(port=self._port, baudrate=self._baudrate, timeout=1)
        msg = ""
        start_time = time.time()
        while not msg.startswith("Chanoscopio"):
            try:
                msg = serial.readline().decode('utf-8')
            except UnicodeDecodeError:
                pass
            if time.time() - start_time > 5:
                raise TimeoutError("Arduino is not responding")
        return serial

    def turn_on_led(self, row: int, column: int, color: str, time: int = 0):
        color_values = {'r': 0, 'g': 1, 'b':2, 'w':3, 'y':4}
        color = color_values[color]
        self._serial.write(row.to_bytes(1, byteorder="little", signed=False))
        self._serial.write(time.to_bytes(1, byteorder="little", signed=False))
        self._serial.write(color.to_bytes(1, byteorder="little", signed=False))
        pass

    def turn_off_leds(self):
        pass

if __name__ == "__main__":
    driver = AnilloDriver("/dev/ttyACM0")
    for i in range(16):
        for color in ["r", "g", "b"]:
            print(i, color)
            driver.turn_on_led(i, 0, color, 1)
            sleep(0.1)

