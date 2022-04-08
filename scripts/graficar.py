import matplotlib.pyplot as plt
import numpy as np

a = np.loadtxt("prueba.csv")
print(a.shape)

plt.imshow(a)
plt.show()
