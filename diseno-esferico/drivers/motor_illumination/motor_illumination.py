from abc import ABC, abstractmethod
from serial import Serial
from dataclasses import dataclass
import time

BAUDRATE = 115200

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

@dataclass(frozen=True)
class MotorIllumination(Illumination):
    _port: str
    _baudrate: int = BAUDRATE
    _color_values: dict = {'r':0, 'g':1, 'b':2}
    _led_pins = dict = {'r':(), 'g':(9, 10, 11, 12, 13), 'b':()}

    def __init__(self, port: str, led_pins: dict = {'r':(), 'g':(9, 10, 11, 12, 13), 'b':()}):
        self._serial = self._open_serial()

    def turn_off_leds(self):
        self._serial.write("LEDS OFF\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response

    def turn_on_led(self, led_no: int, color: str, time: int = 0):
        color = self._color_values[color]
        self._serial.write(f"LED ON {led_no}\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response

    def _set_color(self, color: str):
        """ In the future: shoud select the correct color arm """

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


if __name__ == "__main__":
    motor_ill = MotorIllumination("/dev/ttyACM0")
    print(motor_ill)


