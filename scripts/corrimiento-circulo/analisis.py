import numpy as np 
from pathlib import Path
import matplotlib.pyplot as plt

p = Path(".")

leds = ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]
leds_2 = ["10", "11", "12", "13", "14", "15", "16", "17"]

px_x_guardar = []
for led in leds_2:
    #path_chico = "corrimiento-circulo/imagenes/18_"+led+".npy"
    path_chico = "corrimiento-circulo/imagenes/18_"+led+"_12cm.npy"
    img = np.load(p/path_chico)
    img[img < 150] = 0
    img[img >= 150] = 1
    #print(np.shape(np.where(img == 1)))
    pix_1 = np.array(np.where(img == 1))
    #print(np.where(pix_1 == np.max(pix_1[1,:])))
    px_x = np.max(pix_1[1,:])
    px_x_guardar.append(px_x)

print(px_x_guardar)
print(np.diff(px_x_guardar))
dif = np.diff(px_x_guardar)
print(np.mean(dif), np.std(dif))
print(type(px_x_guardar))
plt.hist(dif, edgecolor = 'k')
plt.show()

def calculo_y(array):
    distancias = []
    for i in range(len(array)):
        dist = np.sqrt(12**2 + np.abs(array[i]-16)*6) ## calculo en mm
        distancias.append(dist)
    return distancias

dist = calculo_y(px_x_guardar) # dist z  = 275mm
plt.plot(px_x_guardar, dist, 'ko')
plt.xlabel('corrimiento en x[px]')
plt.ylabel('distancias [mm]')
plt.show()

