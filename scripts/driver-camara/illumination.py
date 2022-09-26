import time
import random
from serial import Serial  # type: ignore
from typing import List, Dict, Literal
from abc import ABC, abstractmethod

BAUDRATE = 115200
N_LEDS = 32

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


class IlluminationDriver(Illumination):
    def __init__(self, port: str):
        """ RGB Panel driver for Arduino

        Args:
            port (str): Connection port of Arduino, like "/dev/ttyUS0"
        """
        if not isinstance(port, str):
            raise TypeError

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
        """ Turns on the `color` led for desired `row` and `column`

        Note: The argument `time` is an experimental timeout.
        Possible values are 0 to 7 and are codified into Arduino.
        """

        color_values = {'r': 1, 'g': 2, 'b': 4}

        if row < 0 or row >= N_LEDS:
            raise ValueError(f"Valid range: 0 <= row < {N_LEDS:d}")

        if column < 0 or column >= N_LEDS:
            raise ValueError(f"Valid range: 0 <= column < {N_LEDS:d}")

        if any([x not in ['r', 'g', 'b'] for x in color.lower()]):
            raise ValueError("Possible values for colors are: 'r', 'g', 'b'")

        if time < 0 or time > 7:
            raise ValueError("Valid range: 0 <= time < 7")

        encoded_colors = sum(
            [
                color_values[c]
                for c in set([x.lower() for x in color])
            ]
        )

        second_byte = column + (encoded_colors << 5)
        first_byte = row + (time << 5)

        encoded_data = int((first_byte << 8) + second_byte)
        self._serial.write(encoded_data.to_bytes(2, byteorder="little", signed=False))

    def turn_off_leds(self):
        self.turn_on_led(0, 0, "", 0)


class DummyIlluminationDriver(Illumination):
    def __init__(self, port: str):
        self._port = port

    def turn_on_led(self, row: int, column: int, color: str, time: int = 0):
        pass

    def turn_off_leds(self):
        pass


if __name__ == "__main__":
    driver = IlluminationDriver(port="/dev/ttyACM0")

    for y in range(0, 32):
        for x in range(0, 32):
            for color in ["r", "g", "b"]:
                driver.turn_on_led(y, x, color)
                time.sleep(0.01)
