import numpy as np
import matplotlib.pyplot as plt

def normalizar(img):
    maximo = np.max(img)
    img = img/maximo
    return img

img = np.load("/home/chanoscopio/fpm_samples/22_junio/16_16_g_26746.npy")
#img = np.load("matricesMVLD/m_ML.npy")
print(img)
#plt.imshow(img, origin="lower", interpolation="none", vmin=np.min(img), vmax=np.max(img))
plt.imshow(img, cmap = 'gray', vmin=np.min(img), vmax=np.max(img))
plt.show()

print(np.max(img), np.min(img), np.mean(img))
