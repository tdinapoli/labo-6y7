import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def Gauss(x, x0, A, B):
    y = A*np.exp(-1*B*(x-x0)**2)
    return y

colores = ['azul', 'rojo', 'verde', 'blanco']
matriz = []
ajustes = []
p_inicial = [[400, 0.4, 1], [520, 0.24, 1], [640, 0.6, 1]]
for i, color  in  enumerate(colores):
    matriz.append(np.loadtxt(open('espectros_csv/espectro-'+ color + '-anillo.csv').readlines()[:-1], skiprows=34, delimiter=";"))
    data = np.loadtxt(open('espectros_csv/espectro-'+ color + '-anillo.csv').readlines()[:-1], skiprows=34, delimiter=";")
    if color != 'blanco':
        popt, pcov = curve_fit(Gauss, data[:,0], data[:, 1], p0 = p_inicial[i] )
        ajustes.append(popt)

x_varios = np.linspace(400,800, 1000)
colr_graph = ['b', 'r', 'g', 'k']
for i in range(len(matriz)-1):
    x, y = matriz[i][:, 0], matriz[i][:, 1]
    plt.plot(x, y, colr_graph[i], label = colores[i], linestyle ='dotted')
    if i!= 3:
        plt.plot(x_varios, Gauss(x_varios, *ajustes[i]), color = colr_graph[i])

plt.legend()
plt.xlim([400, 800])
plt.show()
