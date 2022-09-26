from camdriver import ImperxCamera
from illumination import IlluminationDriver
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

cam = ImperxCamera()
ill = IlluminationDriver(port="/dev/ttyACM0")
cam.set_gain_exposure(100.0, 25000)
path = None

inp = None
cm = None

while inp != "q":
    inp = input("Opciones:\nc=tomar imagen\np=setear path\ns=tomar imagen y guardarla\nl=setear led\na=apagar leds\ne=setear exposicion\nm=definir cm\nq=salir\n")
    print(f"ingresado: {inp}\n")

    if inp == "c":
        img = cam.get_frame()
        plt.imshow(img, cmap="gray")
        plt.show()
    elif inp == "p":
        path = input("ingresar path:\n")
        path = Path(path)
        print(f"path ingresado: {path}\n")
    elif inp == "s":
        if path:
            img = cam.get_frame()
            name = input("igresar nombre:\n")
            if name == "" and cm:
                x_name, y_name = str(x).zfill(2), str(y).zfill(2)
                cm_name = str(cm)
                name = f"{x_name}_{y_name}_{cm_name}"
                print(f"{name}\n")
            print(f"nombre: {path/name}")
            np.save(path/name, img)
            plt.imshow(img, cmap="gray")
            plt.show()
        else:
            print("path no definido\n")
    elif inp == "l":
        x = input("x: ")
        print(f"{x}\n")
        y = input("y: ")
        print(f"{y}\n")
        x, y = int(x), int(y)
        color = input("color (r, g, b): ")
        print(f"{color}\n")
        ill.turn_on_led(y, x, color)
    elif inp == "a":
        ill.turn_off_leds()
    elif inp == "e":
        exposure = input("ingrese exposicion: ")
        print(f"{exposure}\n")
        exposure = float(exposure)
        cam.set_gain_exposure(100.0, exposure)
    elif inp == "m":
        cm = input("cm: ")
        print(f"{cm}\n")
        cm = int(cm)
    else:
        print("comando no valido\n")


        



