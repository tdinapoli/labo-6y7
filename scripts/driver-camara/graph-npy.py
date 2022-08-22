import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate2d
import imageio

def normalizar(img):
    maximo = np.max(img)
    img = img/maximo
    return img

#img = np.load("/home/chanoscopio/fpm_samples/22_junio/16_16_g_26746.npy")
img = np.load("scripts/epi-iluminacion/comparacion-anillo-transmision.npy")[:, 2000:7000]
kernel = imageio.imread("~/fpm_samples/segunda_rec/Reconstruction/b/magnitude/07_18.tif")
#img = np.load("matricesMVLD/b_MD.npy")
print(img)
#plt.imshow(img, origin="lower", interpolation="none", vmin=np.min(img), vmax=np.max(img))
#plt.imshow(img, cmap = 'gray', vmin=np.min(img), vmax=np.max(img))
#plt.show()

cor = correlate2d(img, kernel)

fig, axs = plt.subplots(1,3)
ax1, ax2, ax3 = axs
ax1.imshow(kernel)
ax2.imshow(img)
ax3.imshow(cor)
plt.show()

print(np.max(img), np.min(img), np.mean(img), np.std(img))
