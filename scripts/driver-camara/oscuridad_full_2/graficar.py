import numpy as np
import matplotlib.pyplot as plt


def histograma(path, alpha=1, t_exp=0):
    imagen = np.load(path)
    hist, bin_edges = np.histogram(imagen, bins=200, density=True)
    bin_width = (bin_edges[1] - bin_edges[0])

    print(np.max(imagen), np.min(imagen), np.var(imagen))

    plt.title("cuentas en oscuridad", fontsize=15)
    plt.xlabel("Pixel Value", fontsize=15)
    plt.bar(bin_edges[:-1], hist, width = bin_width, alpha=alpha, label="T exp "+str(t_exp)+"us")


histograma('im_mean_40000.0.npy', t_exp=40000)
histograma('im_mean_15.0.npy', 0.6, t_exp=15)
plt.legend(fontsize=15)
plt.xlim([150, 200])
plt.show()
#means = np.load('promedio_imagen_de_promedios.npy')
#var = np.load('varianzas_imagen_de_promedios.npy')
#t_exp = np.load('exp_times.npy')
#
#means_nuevo = []
#for i in range(len(means)-1):
#    means_nuevo.append(means[i]-means[i+1])
#    
#
#print(means)
#
#plt.plot(t_exp, means,'ko')
#plt.xlabel('tiempo de exposicion [us]')
#plt.ylabel('promedios')
#plt.show()
#
#plt.plot(t_exp, var,'ko')
#plt.xlabel('tiempo de exposicion [us]')
#plt.ylabel('varianzas')
#plt.show()
#
#
