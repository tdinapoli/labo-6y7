import numpy as np
import matplotlib.pyplot as plt

im = np.load("oscuridad_black_level.npy")
mx, mi = im.max(), im.min()
hist, bin_edges = np.histogram(im, bins=mx- mi, range=(mi,mx), density=False)

plt.plot(bin_edges[:-1], hist, 'ok')
plt.show()
