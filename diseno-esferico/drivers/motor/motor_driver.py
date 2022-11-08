from abc import ABC, abstractmethod
from serial import Serial
import time

BAUDRATE = 115200

class Motor(ABC):
    microsteps: int = 1
    steps: int = 200

    @abstractmethod
    def __init__(self, port: str):
        self.min_angle = 360 / (self.microsteps * self.steps)
        pass

    @abstractmethod
    def rotate(self, degrees: float):
        pass

    @abstractmethod
    def set_rpm(self, velocity: float):
        pass

class MotorEsferico(Motor):
    def __init__(self, port: str):
        super().__init__(port)
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
        pass

    def rotate(self, degrees):
 # Actualmente los grados no se corresponden con el giro del motor 

        self._serial.write(f"THETA {degrees}\n".encode("ascii"))
        response = self._serial.readline().decode("ascii")
        return response
    
    def clean_serial(self):
        while self._serial.in_waiting:
            self._serial.readline().decode('ascii')

    def get_theta(self):
        self.clean_serial()
        self._serial.write("THETA?\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response



if __name__ == "__main__":
    motor = MotorEsferico("/dev/ttyACM0")
    for i in range(10):
        response = motor.rotate(180)
        #print(response)
        print("THETA: ", motor.get_theta())
        time.sleep(1)
        response = motor.rotate(10)
        time.sleep(1)
        #print(motor._serial.readline().decode('ascii'))
        #print(response)
        print("THETA: ", motor.get_theta())

#    while True:
#        response = motor.rotate(360)
#        print(motor._serial.readline().decode('ascii'))
#        time.sleep(1)
#        print(response)

