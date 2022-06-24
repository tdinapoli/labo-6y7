import numpy as np
import matplotlib.pyplot as plt


colores = ['azul', 'rojo', 'verde', 'blanco']
matriz = []
for color in  colores:
    matriz.append(np.loadtxt(open('espectros_csv/espectro-'+ color + '-matriz.csv').readlines()[:-1], skiprows=34, delimiter=";"))

colr_graph = ['b', 'r', 'g', 'k']
for i in range(len(matriz)):
    x, y = matriz[i][:, 0], matriz[i][:, 1]
    plt.plot(x, y, colr_graph[i], label = colores[i])

plt.legend()
plt.xlim([400, 800])
plt.show()
