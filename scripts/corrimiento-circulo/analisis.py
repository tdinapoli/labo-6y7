import numpy as np 
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

p = Path(".")

leds = ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]
leds_2 = ["10", "11", "12", "13", "14", "15", "16", "17"]

led_20 = np.arange(9,19,1)
led_17 = np.arange(10,18,1)
led_11 = np.arange(12, 18,1)
led_6 = np.arange(14, 18,1)


px_x_guardar = []
for led in leds_2:
    #path_chico = "corrimiento-circulo/imagenes/18_"+led+".npy"
    path_chico = "imagenes/18_"+led+"_12cm.npy"
    #led_name = str(led).zfill(2)
    #path_chico = f"imagenes_nuevas/16_{led_name}_20cm.npy"
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

def guardar_data(leds, dist):
    px_x_guardar = []
    for led in leds:
        led_name = str(led).zfill(2)
        path_chico = f"imagenes_nuevas/16_{led_name}_{dist}cm.npy"
        img = np.load(p/path_chico)
        img[img < 150] = 0
        img[img >= 150] = 1
        #print(np.shape(np.where(img == 1)))
        pix_1 = np.array(np.where(img == 1))
        #print(np.where(pix_1 == np.max(pix_1[1,:])))
        px_x = np.max(pix_1[1,:])
        px_x_guardar.append(px_x)
    return px_x_guardar

def calculo_y(array):
    distancias = []
    for i in range(len(array)):
        dist = 6*(array[i] - 16)
        distancias.append(dist)
    return np.array(distancias)

def lineal(x,m,b):
    y = m*x+b
    return y

def calc_kx(L, px_x, arange):
    
    wavelength = 500e-6
    px_size = 3.2*1e-3
    dist_sensor_x = px_size * (np.array(px_x) - 9344/2)
    dist = calculo_y(arange) # dist z  = 165mm
    #kx = (1/np.sqrt((L/dist)**2 + 1))
    kx = (np.cos(np.arctan2(L, dist)))
    
    return kx, dist_sensor_x
#L = 275
##L = 180 o 165
#wavelength = 500e-6
#px_size = 3.2*1e-3
#dist_sensor_x = px_size * (np.array(px_x_guardar) - 9344/2)
##dist = calculo_y(np.arange(7, 18, 1)) # dist z  = 275mm
#dist = calculo_y(np.arange(10, 18, 1)) # dist z  = 165mm
##dist = calculo_y(led_17)
#kx = (1/np.sqrt((L/dist)**2 + 1))
#kx = (np.cos(np.arctan2(L, dist)))
#print(px_x_guardar)


px_x_guardar =  guardar_data(led_11[1:], 11)
kx, dist_sensor_x = calc_kx(110, px_x_guardar, led_11[1:])

popt, pcov = curve_fit(lineal,kx, dist_sensor_x )
m, b = popt
print(popt)

plt.plot(kx, dist_sensor_x, 'ko')
plt.plot(kx, lineal(kx, m, b), 'r', label=f"pendiente = {np.round(m)} mm\n ordenada = {np.round(b, 1)} mm")
plt.xlabel('kx/|k|')
plt.ylabel('x sensor [mm]')
plt.legend()
plt.show()


