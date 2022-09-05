import numpy as np
import matplotlib.pyplot as plt
from interfaces_mod import LedMatrixFpmImageMetadata, LedMatrixFpmConfig, SphericalModuleMetadata, SphericalModuleConfig
import pathlib

def graph_support(k_vectors, NA):
    fig, ax = plt.subplots(1)
    radio = NA * np.linalg.norm(k_vectors[0])
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        ax.scatter(kx, ky, s=0.5, color="black")
        circle = plt.Circle((kx, ky), radio, alpha=0.2, linewidth=0.2)
        ax.set_aspect(1)
        ax.add_artist(circle)
    k_vectors = np.array(k_vectors)
    ax.set_xlim([min(k_vectors[:, 0]) - radio, max(k_vectors[:,0]) + radio])
    ax.set_ylim([min(k_vectors[:, 1]) - radio, max(k_vectors[:,1]) + radio])

def create_circular_mask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[-h//2:h//2, -w//2:w//2]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1] )**2)

    mask = dist_from_center <= radius
    return mask

def overlap(k_vectors, NA, freq_per_pix=1.6e4, shape=(1000,1000)):
    fig, ax = plt.subplots(1)
    k_vectors = np.array(k_vectors)/freq_per_pix
    radius = NA * np.linalg.norm(k_vectors[0])
    img = np.zeros(shape=shape, dtype=int)
    shapex, shapey = shape
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        msk = create_circular_mask(shapex, shapey, center=(kx, ky), radius=radius)
        img[msk] = img[msk] + 1

    img[:,img.shape[1]//2 ] = 0
    pos = ax.imshow(img)
    fig.colorbar(pos, ax=ax)
    return img

path = pathlib.Path("./configs/")
print(path.absolute())

mat_cfg = LedMatrixFpmConfig.from_path(path/"mat")
print(mat_cfg)

sph_cfg = SphericalModuleConfig.from_path(path / "sph")
print(sph_cfg)

########################### calculo vectores y posiciones matriz ###################

def calculate_mat(led_amount, c_x, c_y):
    k_vecs_mat = []
    led_pos_mat = []

    for i in range(c_x-led_amount, c_x+ led_amount+1):
        for j in range(c_y-led_amount, c_y+ led_amount+1):
            led_pos = mat_cfg.calculate_led_pos((i, j))
            k_vec = np.array(mat_cfg.calculate_wavevector(
                    led_pos,
                    patch_center_px=(0, 0)
                    ))
            k_vecs_mat.append(k_vec)
            led_pos_mat.append(led_pos)
    return k_vecs_mat, led_pos_mat

c_x, c_y = mat_cfg.center
led_amount = 5
k_vecs_mat, led_pos_mat = calculate_mat(led_amount, c_x, c_y)

########################### calculo vectores y posiciones esfera ###################

def calculate_sph(phi_steps, n_leds):
    k_vecs_sph = []
    led_pos_sph = []

    for step in range(phi_steps):
        for led in range(n_leds):
            led_pos = sph_cfg.calculate_led_pos(led, step)
            k_vec = np.array(sph_cfg.calculate_wavevector(
                led_pos,
                patch_center_px=(sph_cfg.image_size[0]//2, sph_cfg.image_size[1]//2)
                ))
            k_vecs_sph.append(k_vec)
            led_pos_sph.append(led_pos)
    return k_vecs_sph, led_pos_sph

k_vecs_sph, led_pos_sph = calculate_sph(sph_cfg.phi_steps, sph_cfg.n_leds)

########################### gráfico 3d MATRIZ ###############################
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
ax.set_xlim([-100, 100])
ax.set_ylim([-100, 100])
ax.set_zlim([-250, -50])
ax.scatter(0,0,0, color="k", s=30)

vector_length = 10
for led_pos, k_vec in zip(led_pos_mat, k_vecs_mat):
    x, y, z = led_pos
    kx, ky, kz = vector_length * k_vec / np.linalg.norm(k_vec)
    ax.scatter(x, y, z, color="tab:orange")
    ax.quiver(x, y, z, kx, ky, kz, linewidth=1, color="tab:blue")

########################### gráfico 3d ESFERA ###############################

for led_pos, k_vec in zip(led_pos_sph, k_vecs_sph):
    x, y, z = led_pos
    kx, ky, kz = vector_length * k_vec / np.linalg.norm(k_vec)
    ax.scatter(x,y,z, color="tab:red")
    ax.quiver(x,y,z,kx,ky,kz, color="tab:blue")

plt.show()

########################### gráfico overlap sph y mat ##############################

freq_per_pix=2.5e4
shape=(1000,1000)
overlap(k_vecs_sph, sph_cfg.objective_na, freq_per_pix=freq_per_pix, shape=shape)
plt.show()
overlap(k_vecs_mat, mat_cfg.objective_na, freq_per_pix=freq_per_pix, shape=shape)
plt.show()

########################### Overlap para radios ############################## (HAY QUE BORRAR FROZEN=TRUE)

max_leds = 20
n_leds_list = np.arange(1, max_leds + 1, 1, dtype=int)

fpp = 2.5e4
ol_pcts = []

for n_leds in n_leds_list:
    sph_cfg.n_leds = n_leds
    k_vecs_sph, led_pos_sph = calculate_sph(1, n_leds)
    ol = overlap(k_vecs_sph, sph_cfg.objective_na, freq_per_pix=fpp)
    ol_pct = []
    covered_area = np.count_nonzero(ol >= 1)
    for ol_n in range(1, np.max(ol)):
        ol_pct.append(np.count_nonzero(ol > ol_n)/ covered_area) 
    ol_pcts.append(ol_pct)
plt.show()

for ol_pct in ol_pcts:
    plt.plot(np.arange(1, len(ol_pct) + 1, 1, dtype=int), ol_pct)
plt.show()



