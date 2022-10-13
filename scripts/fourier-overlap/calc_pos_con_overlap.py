import numpy as np
import matplotlib.pyplot as plt
import pathlib
import sys
import os

sys.path.append("/home/chanoscopio/git/labo-6y7/scripts/fourier-overlap/sph_illumination/")

from interfaces_mod import SphericalModuleConfig


def calculate_position_sph(z0, R, tita, fi0, n_leds, m, n): # units in mm
    fim = m * fi0
    x = R * np.cos(m*fi0) * np.sin(tita)
    y = R * np.sin(m*fi0) * np.sin(tita)
    z = -z0 + R*np.cos(tita)
    return np.array([x, y, z])

def calculate_position_sph_any(z0, R, tita, fi): # units in mm
    x = R * np.cos(fi) * np.sin(tita)
    y = R * np.sin(fi) * np.sin(tita)
    z = -z0 - R*np.cos(tita)
    return np.array([x, y, z])

def calculate_k_vector_general(led_position, wavelength, offset=np.array([0,0,0])):
    x, y, z = led_position - offset
    #k_0 = 2*np.pi/wavelength
    k_0 = 1/wavelength
    module = np.linalg.norm(np.array([x,y,z]))
    kx = -x/module
    ky = -y/module
    kz = -z/module
    k_vector = np.array([kx,ky,kz])*k_0
    return k_vector


def overlap(k_vectors, NA, freq_per_pix=1e3, shape=(3000,3000)):
    #fig, ax = plt.subplots(1)
    k_vectors = np.array(k_vectors)/freq_per_pix
    radius = NA * np.linalg.norm(k_vectors[0])
    img = np.zeros(shape=shape)
    shapex, shapey = shape
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        msk = create_circular_mask(shapex, shapey, center=(kx, ky), radius=radius)
        img[msk] = img[msk] + 1
    #img[:, 499:501] = 0
    #pos = ax.imshow(img)
    #fig.colorbar(pos, ax=ax)
    #plt.show()
    #ax.set_title("wavelength="+str(wavelength)+"m\nfreq_per_pix="+str(freq_per_pix)+"$m^{-1}$"+"\n n_fotos="+str(len(k_vectors)))
    return img

def overlap_w_image(k_vectors, NA, freq_per_pix=1e3, shape=(3000,3000)):
    #fig, ax = plt.subplots(1)
    k_vectors = np.array(k_vectors)/freq_per_pix
    radius = NA * np.linalg.norm(k_vectors[0])
    img = np.zeros(shape=shape)
    shapex, shapey = shape
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        msk = create_circular_mask(shapex, shapey, center=(kx, ky), radius=radius)
        img[msk] = img[msk] + 1
    img[:, 499:501] = 0
    #pos = plt.figure.canvas.imshow(img)
    #fig.colorbar(pos, ax=ax)
    #plt.show()
    #ax.set_title("wavelength="+str(wavelength)+"m\nfreq_per_pix="+str(freq_per_pix)+"$m^{-1}$"+"\n n_fotos="+str(len(k_vectors)))
    return img

def create_circular_mask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[-h//2:h//2, -w//2:w//2]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1] )**2)

    mask = dist_from_center <= radius
    return mask

z0 = 0
R = 90
tita = 0
fi0 = 0
m = 0
n = 0
n_leds = 5
wavelength=500e-9
NA = 0.1
tita_max = np.pi/3


pos = calculate_position_sph(z0, R, tita, fi0, n_leds, m, n)
k = calculate_k_vector_general(pos, wavelength=wavelength)

radius = NA * np.linalg.norm(k)/(2*np.pi)

ks = [k]

expected_overlap = 0.3
tolerance = 0.01
jump = 0.0005 * tita_max
tita = tita + jump
guess = calculate_position_sph(z0, R, tita, fi0,n_leds, m, n)
guess_k = calculate_k_vector_general(guess, wavelength=wavelength)
ks.append(guess_k)
ol = overlap(ks, NA)
covered_area = np.count_nonzero(ol >= 1)
ol_pct = np.count_nonzero(ol>1)/covered_area
titas = []
ol_pcts = []
for i in range(10):
    while np.abs(ol_pct - expected_overlap) > tolerance and tita < tita_max:
        tita = tita + jump
        pos_nueva = calculate_position_sph(z0, R, tita, fi0,n_leds, m, n)
        k_nuevo = calculate_k_vector_general(pos_nueva, wavelength = wavelength)
        ks[1] = k_nuevo

        ol = overlap(ks, NA)
        ol_pct = np.count_nonzero(ol > 1)/covered_area
        print(i, ol_pct)

    titas.append(tita)
    ol_pcts.append(ol_pct)
    guess = calculate_position_sph(z0, R, tita, fi0,n_leds, m, n)
    guess_k = calculate_k_vector_general(guess, wavelength=wavelength)
    ks = [k_nuevo, k_nuevo]
#    ks[0] = ks[1]
#    ks[1] = guess_k
    ol = overlap_w_image(ks, NA)
    ol_pct = np.count_nonzero(ol>1)/covered_area
#    print("KAS",ks)
#    print("TITA", tita)
#plt.show()


print("OL PCTs", ol_pcts)
print("TITAS", titas )

## Graficar posicioens de los leds para los titas calculados
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlim([-100, 100])
ax.set_ylim([-100, 100])
ax.set_zlim([-250, -50])
ax.scatter(0,0,0, color="k", s=30)
fi = 0
R = 130
z0 = 0
for tita in titas:
    print(tita, *pos)
    pos = calculate_position_sph_any(z0, R, tita, fi)
    ax.scatter(*pos, color="tab:orange")
plt.show()



