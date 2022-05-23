import numpy as np
import matplotlib.pyplot as plt
#exp_times = [15.0,10000.0,20000.0,30000.0,40000.0] rel a "med_viejas"
exp_times = list(np.load('oscuridad_full_2/exp_times.npy'))
means_tot = []
var_tot = []
for i in exp_times:
    mean = np.load("oscuridad_full_2/im_mean_"+str(i)+".npy")
    var = np.load("oscuridad_full_2/im_var_"+str(i)+".npy")
    mean_mean = np.mean(mean)
    var_mean = np.mean(var)
    means_tot.append(mean_mean)
    var_tot.append(var_mean)
    print(i," vuelta")

np.save('promedio_imagen_de_promedios', means_tot)
np.save('varianzas_imagen_de_promedios', var_tot)
plt.plot(exp_times, means_tot, 'ko')
plt.xlabel('tiempo de exposicion[micro segundos]')
plt.ylabel('pixel promedio del promedio de 50 imágenes [ADU]')
plt.show()

   # plt.imshow(mean, cmap="gray")
   # plt.colorbar()
   # plt.show()
   # plt.imshow(var)
   # plt.colorbar()
   # plt.show()

