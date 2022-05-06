import matplotlib.pyplot as plt
import numpy as np

oscuridad = np.load("means_oscuridad.npy")
stds = np.load("stds_oscuridad.npy")
t_exp = np.load("tiempos_de_exposicion_oscuridad.npy")

print(oscuridad.shape)
print(stds.shape)
print(t_exp.shape)

means_total = np.mean(oscuridad, axis = 1)
std_total = np.mean(stds, axis = 1)

plt.errorbar(t_exp, means_total, yerr = std_total)
plt.show()
