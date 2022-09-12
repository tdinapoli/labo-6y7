import numpy as np 
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

p = Path(".")

leds = ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]
leds_2 = ["10", "11", "12", "13", "14", "15", "16", "17"]

px_x_guardar = []
for led in leds:
    path_chico = "corrimiento-circulo/imagenes/18_"+led+".npy"
    #path_chico = "corrimiento-circulo/imagenes/18_"+led+"_12cm.npy"
    img = np.load(p/path_chico)
    img[img < 150] = 0
    img[img >= 150] = 1
    #print(np.shape(np.where(img == 1)))
    pix_1 = np.array(np.where(img == 1))
    #print(np.where(pix_1 == np.max(pix_1[1,:])))
    px_x = np.max(pix_1[1,:])
    px_x_guardar.append(px_x)

print(px_x_guardar)
dif = np.diff(px_x_guardar)
print(np.mean(dif), np.std(dif))
print(type(px_x_guardar))

def calculo_y(array):
    distancias = []
    for i in range(len(array)):
        dist = 6*(array[i] - 16)
        distancias.append(dist)
    return np.array(distancias)

def lineal(x,m,b):
    y = m*x+b
    return y

L = 275
#L = 180 o 165
wavelength = 500e-6
px_size = 3.2*1e-3
dist_sensor_x = px_size * (np.array(px_x_guardar) - 9344/2)
dist = calculo_y(np.arange(7, 18, 1)) # dist z  = 275mm
#dist = calculo_y(np.arange(10, 18, 1)) # dist z  = 165mm
kx = (1/np.sqrt((L/dist)**2 + 1))
kx = (np.cos(np.arctan2(L, dist)))
print(px_x_guardar)

popt, pcov = curve_fit(lineal,kx, dist_sensor_x )
m, b = popt
print(popt)

plt.plot(kx, dist_sensor_x, 'ko')
plt.plot(kx, lineal(kx, m, b), 'r', label=f"pendiente = {np.round(m)} mm\n ordenada = {np.round(b, 1)} mm")
plt.xlabel('kx/|k|')
plt.ylabel('x sensor [mm]')
plt.legend()
plt.show()


