import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import correlate2d
import imageio

def normalizar(img):
    maximo = np.max(img)
    img = img/maximo
    return img

#img = np.load("/home/chanoscopio/fpm_samples/22_junio/16_16_g_26746.npy")
img = np.load("epi-iluminacion/comparacion-igual-matriz.npy")[3000:4000, 4000:5000]
#kernel = imageio.imread("~/fpm_samples/segunda_rec/Reconstruction/b/magnitude/07_18.tif")
#img = np.load("matricesMVLD/b_MD.npy")
print(img)
#plt.imshow(img, origin="lower", interpolation="none", vmin=np.min(img), vmax=np.max(img))
#plt.imshow(img, cmap = 'gray', vmin=np.min(img), vmax=np.max(img))
#plt.show()

#cor = correlate2d(img, kernel)

fig, axs = plt.subplots(1)
#ax1, ax2, ax3 = axs
#ax1.imshow(kernel)
axs.imshow(img, cmap ='gray')
axs.get_xaxis().set_visible(False)
axs.get_yaxis().set_visible(False)
#ax3.imshow(cor)
#plt.savefig('zoom_poster.pdf')
plt.show()

print(np.max(img), np.min(img), np.mean(img), np.std(img))
