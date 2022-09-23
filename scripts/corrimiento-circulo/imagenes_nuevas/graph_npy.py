import numpy as np
import matplotlib.pyplot as plt

im = np.load('16_16_11cm.npy')
plt.imshow(im, cmap = 'gray')
plt.show()
