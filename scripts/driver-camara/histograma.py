import numpy as np
import matplotlib.pyplot as plt

im = np.load("matricesMVLD/dark/mean_1000000.npy")
mx, mi = im.max(), im.min()
mx, mi = round(mx), round(mi)
hist, bin_edges = np.histogram(im, bins=mx- mi, range=(mi,mx), density=False)

#plt.plot(bin_edges[:-1], hist, 'ok')

im = np.load("matricesMVLD/dark/mean_15.npy")
mx, mi = im.max(), im.min()
mx, mi = round(mx), round(mi)
hist, bin_edges = np.histogram(im, bins=mx- mi, range=(mi,mx), density=False)

plt.hist(hist, bins = bin_edges)

plt.xlim([150,200])
plt.show()
