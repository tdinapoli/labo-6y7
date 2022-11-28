from abc import ABC, abstractmethod
from serial import Serial
import time as pytime
import numpy as np
import threading
BAUDRATE = 115200

def dummy_func():
    return

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

class SphericalController(Motor, Illumination):
    def __init__(self, port: str, led_pins: dict = None):
        super().__init__(port)
        self._port = port
        self._baudrate = BAUDRATE
        self._serial = self._open_serial()

        # INIT LEDS
        self._color_values = {'r':0, 'g':1, 'b':2}
        self.led_pins = led_pins
        if not self.led_pins:
            self.led_pins = {'r':(), 'g':(2, 3, 4, 5, 6, 7, 10), 'b':()} 

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.turn_off_leds()
        self.close()

    def __del__(self):
        self.turn_off_leds()

    def _open_serial(self) -> Serial:
        """ Opens a serial port between Arduino and Python """

        serial = Serial(port=self._port, baudrate=self._baudrate, timeout=1)
        msg = ""
        start_time = pytime.time()
        while not msg.startswith("Chanoscopio"):
            try:
                msg = serial.readline().decode('utf-8')
            except UnicodeDecodeError:
                pass
            if pytime.time() - start_time > 5:
                raise TimeoutError("Arduino is not responding")
        return serial

    def close(self):
        self._serial.close()
    
    def set_rpm(self, RPM):
        pass

    def rotate(self, degrees):
 # Actualmente los grados no se corresponden con el giro del motor 

        self._serial.write(f"THETA {degrees}\n".encode("ascii"))
        response = self._serial.readline().decode("ascii")
        return response
    
    def clean_serial(self): # No funciona, cambiar
        while self._serial.in_waiting:
            self._serial.readline().decode('ascii')

    def get_theta(self):
        self.clean_serial()
        self._serial.write("THETA?\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response

    #Position configuring methods

    def rotate_left(self, steps=10):
        self._serial.write(f"STEP {steps}\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response

    def rotate_right(self, steps=-10):
        self._serial.write(f"STEP {steps}\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response

    def set_origin(self):
        self._serial.write('INITIALIZE\n'.encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response



    #LEDS METHODS

    def turn_off_leds(self):
        self._serial.write("OFF\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        return response

    def turn_on_led(self, led_no: int, color: str, time: int = 0):
        color = self._color_values[color]
        self._serial.write(f"ON {led_no}\n".encode('ascii'))
        response = self._serial.readline().decode('ascii')
        #print(response)
        #pytime.sleep(float(time)/1000) # HAY QUE IMPLEMENTAR COLAS PARA QUE NO SEA BLOQUEANTE
        #timer = threading.Timer(float(time), dummy_func)
        #timer.start()
        #self.turn_off_leds()
        return response


if __name__ == "__main__":
    from camera_driver import ImperxCamera 
    import matplotlib.pyplot as plt
    import multiprocessing as mp
    from time import perf_counter

    inicio = perf_counter()


    def save_img(q, imgs):
        for i in range(imgs):
            print(f"on queue: {q.qsize()}")
            name, barr = q.get()
            np.save(name, barr)

    mp.set_start_method("fork")

    camera = ImperxCamera()

    sph = SphericalController("/dev/ttyACM0")
    sph.set_origin()

    phis = np.linspace(0.0, 360.0, 40, dtype=float)

    q = mp.Queue(maxsize=50)
    p = mp.Process(target=save_img, args=(q, len(phis) * len(sph.led_pins["g"]))) # tratar de cambiar para q sea independiente de la cant de fotos
    p.start()
    for phi in phis:
        sph.rotate(phi)
        pytime.sleep(0.5)
        times = np.array([0.2,0.2,0.4,0.4,0.6,0.6,1]) *100
        for led, time in zip(sph.led_pins["g"], times):
            camera.set_gain_exposure(100.0, time*1000.0)
            sph.turn_on_led(led, "g", time)
            pytime.sleep(0.05) 
            imagen = camera.get_frame()
            q.put((f'prueba_lentitud/led_{led}_angulo_{phi}.npy', imagen))
#
           # p.join()
            #np.save(f'prueba_lentitud/led_{led}_angulo_{phi}.npy', imagen)
            #plt.imshow(imagen, cmap = 'gray')
            #plt.show()

    sph.rotate(0)
    sph.turn_off_leds()
    print(perf_counter() - inicio , len(phis) * len(sph.led_pins["g"]) )
    #camera.close()
            
