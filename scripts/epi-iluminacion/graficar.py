import numpy as np
import matplotlib.pyplot as plt

im_transmision = np.load('comparacion-igual-matriz.npy')
im_refelxion = np.load('comparacion-igual-anillo.npy')

fig, ax = plt.subplots(1,2)
ax[0].imshow(im_transmision[3000:4000, 4000:5000], cmap = 'gray')
#plt.show()

ax[1].imshow(im_refelxion[3000:4000, 4000:5000], cmap = 'gray')
plt.show()
