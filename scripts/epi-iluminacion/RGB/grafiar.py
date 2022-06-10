import numpy as np
import matplotlib.pyplot as plt

colores = ['R', 'G', 'B']

matriz = []
anillo = []

for i in colores:
    matriz.append(np.load('comparacion-igual-matriz_'+i+'.npy'))
    anillo.append(np.load('comparacion-igual-anillo_'+i+'.npy'))

for i, color in enumerate(colores):
    fig, ax = plt.subplots(1,2)
    plt.title(color)
    ax[0].imshow(matriz[i][3000:4000, 4000:5000], cmap = 'gray')

    ax[1].imshow(anillo[i][3000:4000, 4000:5000], cmap = 'gray')
    plt.show()

