import numpy as np
import matplotlib.pyplot as plt

def areaCirculo(R, d):
    """calcula el área de interseccion entre dos circulos de radio R con centros a distancia d

    :R: radio
    :d: distancia entre centros
    :returns: area

    """
    A = 2* R**2 * np.arccos(d/(2*R)) - d * np.sqrt(R**2 - (d/2)**2)
    return A

def calcularArea(led1, led2, lmbd, do, dx, dy, R):
    """Calcula el area de intersección del circulo en el espacio de Fourier generado al prender dos LEDs.

    :led1: Tupla (i, j) que determina el led de la grilla, se asume que (0,0) está en el eje óptico
    :led2: led2
    :lmbd: long de onda
    :do: distancia entre grilla y muestra
    :dx: distancia horizontal entre leds
    :dy: distancia vertical entre leds
    :R: radio en el espacio de fourier dado por el objetivo
    :returns: area de intersección

    """
    modK = 1/lmbd
    i1, j1 = led1
    i2, j2 = led2
    x1, y1 = [j1 * dx, i1*dy]
    x2, y2 = [j2 * dx, i2*dy]

    dij1 = np.sqrt(x1**2 + y1**2) 
    kx1 = modK * np.sin(np.arctan(dij1/do)) * np.cos(np.arctan(y1/x1))
    ky1 = modK * np.sin(np.arctan(dij1/do)) * np.sin(np.arctan(y1/x1))
    kz1 = modK * np.cos(np.arctan(dij1/do))
    k1 = np.array([kx1, ky1, kz1])

    dij2 = np.sqrt(x2**2 + y2**2) 
    kx2 = modK * np.sin(np.arctan(dij2/do)) * np.cos(np.arctan(y2/x2))
    ky2 = modK * np.sin(np.arctan(dij2/do)) * np.sin(np.arctan(y2/x2))
    kz2 = modK * np.cos(np.arctan(dij2/do))
    k2 = np.array([kx2, ky2, kz2])

    dist_entre_circulos = np.linalg.norm(k2 - k1)
    print(1/lmbd)
    print(np.linalg.norm(k1), np.linalg.norm(k2))
    print(dist_entre_circulos)

    area = areaCirculo(R, dist_entre_circulos)
    area_max = np.pi * R**2

    return area/area_max

led1 = (1,2)
led2 = (1,1)
lmbd = 652e-9
do = 0.1
dx = 0.05
dy = 0.05
R = 0.03

print(calcularArea(led1, led2, lmbd, do, dx, dy, R))
#areas = []
#for dist in np.linspace(0, 2, 100):
#    areas.append(areaCirculo(1, dist)/np.pi)
#plt.plot(np.linspace(0,2, 100), areas)
#plt.show()
#    
#
