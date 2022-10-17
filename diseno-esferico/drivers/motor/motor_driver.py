from abc import ABC, abstractmethod
from serial import Serial
import time

BAUDRATE = 115200

class Motor(ABC):
    @abstractmethod
    def __init__(self, port: str):
        pass

    @abstractmethod
    def rotate(self, degrees: float):
        pass

    @abstractmethod
    def set_rpm(self, velocity: float):
        pass

class MotorEsferico(Motor):
    def __init__(self, port: str):
        self._port = port
        self._baudrate = BAUDRATE
        self._serial = self._open_serial()

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
    
    def set_rpm(self, RPM):
        #self._serial.write(bytes("R", 'ascii'))
        #self._serial.write(bytes("r", 'ascii'))
        f1 = 1
        self._serial.write(b'\x01')
        self._serial.write(f1.to_bytes(1, byteorder="little", signed=False))

    def rotate(self, degrees):
        #self._serial.write(bytes("D", 'ascii'))
        self._serial.write(b'\x02')
        self._serial.write(degrees.to_bytes(1, byteorder="little", signed=False))

        

if __name__ == "__main__":
    motor = MotorEsferico("/dev/ttyACM0")
    motor.set_rpm(200)
    #a = motor._serial.read()
    #print(a)
    motor.rotate(100)

