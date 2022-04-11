import matplotlib.pyplot as plt
import numpy as np

a = np.loadtxt("prueba.csv")
print(a)



plt.imshow(a, cmap='gray', vmin = 0, vmax = 255)
plt.show()
