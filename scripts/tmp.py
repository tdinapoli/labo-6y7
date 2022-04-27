import numpy as np
import matplotlib.pyplot as plt

prom1 = np.load("promedios_0.1_igual_1.npy")
prom2 = np.load("promedios_0.1_igual_2.npy")

te1 = np.load("tiempo_de_exposicion_igual_1.npy")
te2 = np.load("tiempo_de_exposicion_2.npy")

plt.figure()
plt.plot(te1, prom1-prom2)
plt.show()

plt.figure()
plt.plot(te1, prom1, 'k.-')
plt.plot(te1, prom2, 'r.-')
plt.show()
