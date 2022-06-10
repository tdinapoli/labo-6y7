import numpy as np
import matplotlib.pyplot as plt

#img = np.load("/home/chanoscopio/fpm_samples/prueba_1_web/16_15_r_34369.npy")
img = np.load("matricesMVLD/m_MD.npy")
print(img)
plt.imshow(img)
plt.show()
