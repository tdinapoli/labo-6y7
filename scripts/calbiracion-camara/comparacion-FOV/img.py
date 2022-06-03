import matplotlib.pyplot as plt
import numpy as np

img = plt.imread('camara_nueva_cuadrado_driver.png')
plt.imshow(img)
plt.show()

ann = 9344
aln = 7000
resn = ann * aln
dxn = 170 - 492
dyn = 140 - 135 
drn = 1
calimn = 0.05283
dxn = dxn/calimn
dyn = dyn/calimn
caln = np.sqrt(dxn**2 + dyn**2)/drn
print(caln)

img = plt.imread('camara_vieja_cuadrado.png')
plt.imshow(img)
plt.show()

anv = 5000
alv = 4000
resv = anv * alv
dxv = 193 - 464
dyv = 135 - 135 
drv = 0.5
calimv = 0.08925
dxv = dxv/calimv
dyv = dyv/calimv
calv = np.sqrt(dxv**2 + dyv**2)/drv
print(calv)

print("ancho nueva", 9344/caln)
print("alto nueva", 7000/caln)
print("area nueva", resn/caln**2)

print("ancho vieja", 4000/calv)
print("alto vieja", 5000/calv)
print("area vieja", resv/calv**2)
