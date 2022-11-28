import sys
from todo_junto.camera_driver import ImperxCamera
import numpy as np
import matplotlib.pyplot as plt

def commands():
    comandos = [
        '0: setear origen',
        'o: prender led' ,
        'l: mover 10 a la izquierda',
        'h: mover 10 a la derecha',
        'a: apagar todos los leds',
        'i: inicializar camara',
        's: guardar foto',
        'c: visualizar foto',
        'q: salir'
    ]
    texto = ''
    for comando in comandos:
        texto = texto + comando + "\n"
    return texto



if __name__ == "__main__":
    from todo_junto.sph_module import SphericalController

    sph = SphericalController("/dev/ttyACM0")

    comando = ''

    while comando != 'q':
        comando = input(commands())
        if comando == '0':
            resp = sph.set_origin()
            print(resp)

        elif comando == 'l':
            resp = sph.rotate_left()
            print(resp)
            
        elif comando == 'h':
            resp = sph.rotate_right()
            print(resp)

        elif comando == 'o':
            led = input('seleccionar led ')
            #tiempo = input('Seleccionar tiempo ')
            resp = sph.turn_on_led(int(led), 'g', 1)
            print(resp)

        elif comando == 'a':
            resp = sph.turn_off_leds()
            print(resp)

        elif comando == "i":
            camera = ImperxCamera()

        elif comando == "s":
            exp = input("Exp time: ")
            camera.set_gain_exposure(100.0, exp)
            imagen = camera.get_frame()
            path = f"/home/chanoscopio/git/labo-6y7/diseno-esferico/exp-time/imagenes/{exp}_oscuridad" 
            print(path)
            np.save(path, imagen)
            print(np.mean(imagen))
            print('max', np.max(imagen))
            print('min', np.min(imagen))
            plt.imshow(imagen, cmap="gray")
            plt.show()

        elif comando == "c":
            imagen = camera.get_frame()
            print(np.mean(imagen))
            print('max', np.max(imagen))
            print('min', np.min(imagen))
            plt.imshow(imagen, cmap="gray")
            plt.show()

        elif comando != 'q':
            print('comando incorrecto')

