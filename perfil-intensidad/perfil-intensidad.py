import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

img = np.load("perfil-intensidad-nada.npy")
img_muestra = np.load("perfil-intensidad-muestra.npy")
img_celular = mpimg.imread('celular_2.jpeg')
perfil = img[3500, :]
perfil_muestra = img_muestra[3500, :]
perfil_celular = img_celular[800, :,2]
pixels = np.arange(0, 9344, 1)
plt.plot(pixels, perfil, color ='r')
plt.plot(pixels, perfil_muestra, color = 'k')
plt.plot(perfil_celular, color = 'b')
plt.show()
