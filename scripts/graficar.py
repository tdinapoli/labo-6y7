import matplotlib.pyplot as plt
import numpy as np

a = np.loadtxt("prueba.csv")
print(a)

for val in np.unique(a):
    print(val)


#plt.imshow(a)
#plt.show()
