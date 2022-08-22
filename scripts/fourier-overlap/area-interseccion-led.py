import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib as mpl

def areaCirculo(R, d):
    """calcula el área de interseccion entre dos circulos de radio R con centros a distancia d

    :R: radio
    :d: distancia entre centros
    :returns: area

    """
    A = 2* R**2 * np.arccos(d/(2*R)) - d * np.sqrt(R**2 - (d/2)**2)
    return A

def calcularArea(led1, led2, lmbd, do, dx, dy, NA):
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

    phi1 = np.arctan2(y1, x1)
    dij1 = np.sqrt(x1**2 + y1**2) 
    tita1 = np.arctan(dij1/do)
    kx1 = modK * np.sin(tita1) * np.cos(phi1)
    ky1 = modK * np.sin(tita1) * np.sin(phi1)
    kz1 = modK * np.cos(np.arctan(dij1/do))
    k1 = np.array([kx1, ky1, kz1])

    phi2 = np.arctan2(y2, x2)
    dij2 = np.sqrt(x2**2 + y2**2) 
    tita2 = np.arctan(dij2/do)
    kx2 = modK * np.sin(tita2) * np.cos(phi2)
    ky2 = modK * np.sin(tita2) * np.sin(phi2)
    kz2 = modK * np.cos(np.arctan(dij2/do))
    k2 = np.array([kx2, ky2, kz2])

    k_radio = NA * modK/2

    dist_entre_circulos = np.linalg.norm(k2 - k1)

    area = areaCirculo(k_radio, dist_entre_circulos)
    area_max = np.pi * k_radio**2


    return area/area_max, dist_entre_circulos,k1,k2

led1 = (1,1)
led2 = (1,2)
lmbd = 652e-9
#dos = [0.05, 0.1, 0.15, 0.2, 0.25]
dos = [0.15]
dx = 0.006
dy = 0.006
NA = 0.1


for do in dos:
    fig, ax = plt.subplots()
    kxs = []
    kys = []
    ks = []
    radio = NA/(lmbd*2)
    for i in range(-15, 16):
        for j in range(-15,16):
            if j != 100:
                led1 = (1,1)
                led2 = (i,j)
                area, dist,k1,k2 = calcularArea(led1, led2, lmbd, do, dx, dy, NA)
                k2x, k2y, k2z = k2
                #circle = plt.Circle((k2[0], k2[1]),radio, fill = False, linewidth = 0.2)
                circle = plt.Circle((k2x, k2y),radio, alpha  = 0.1, linewidth = 0.2)
                #ax.plot(k2x, k2y, '.k')
                kxs.append(k2x)
                kys.append(k2y)
                ks.append(np.array([k2x, k2y]))

                ax.set_aspect(1)
                ax.add_artist(circle)
    ax.scatter(kxs, kys, s=0.1, color="black")
    plt.xlim([-1.25e6, 1.25e6])
    plt.ylim([-1.25e6, 1.25e6])
    plt.title(str(do))
    plt.savefig("overlap_"+str(dos[0])+".png", dpi =1000)
    plt.show()

ks = np.array(ks)
x = np.linspace(-1e6, 1e6, 100)
y = np.linspace(-1e6, 1e6, 100)
cuantos_hay = np.zeros(shape=(len(x), len(y)))

for i in range(len(x)):
    for j in range(len(y)):
        punto_mesh = np.array([x[i], y[j]])
        n_overlap = 0
        for k in ks:
            dist = np.linalg.norm(punto_mesh - k)
            #print(punto_mesh, k, dist, dist < radio)
            if dist < radio:
                n_overlap += 1
        cuantos_hay[i, j] = n_overlap
        

print(radio)
print(cuantos_hay)
#discrete_cmap = [(x, x, x) for x in range(1,)]
cmap = plt.cm.viridis
cmap_list = [cmap(i*23) for i in range(12)]
cmap = mpl.colors.LinearSegmentedColormap.from_list('Custom cmap', cmap_list, 12)
plt.imshow(cuantos_hay, cmap =cmap )
plt.title(str(do))
plt.colorbar()
plt.savefig("Overlap_colormap_"+str(dos[0])+".png", dpi = 1000)
plt.show()





