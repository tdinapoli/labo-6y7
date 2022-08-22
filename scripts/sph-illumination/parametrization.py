import numpy as np
import matplotlib.pyplot as plt

def calculate_positions(z0, R, tita_max, fi0, n_leds, m, n): # units in mm
    fim = m * fi0
    titan = np.pi - tita_max* n/n_leds
    x = R * np.cos(m*fi0) * np.sin(titan)
    y = R * np.sin(m*fi0) * np.sin(titan)
    z = -z0 + R*np.cos(titan)
    return (x, y, z)

def calculate_k_vector(z0, R, tita_max, fi0, n_leds, wavelength,m ,n):
    x, y, z = calculate_positions(z0, R, tita_max, fi0, n_leds, m, n)
    k_0 = 2*np.pi/wavelength
    module = np.linalg.norm(np.array([x,y,z]))
    kx = -x/module
    ky = -y/module
    kz = -z/module
    k_vector = np.array([kx,ky,kz])*k_0
    return k_vector

def calculate_k_vectors(z0, R, tita_max, fi0, n_leds, n_steps, wavelength):
    k_vectors = []
    max_steps = int(2*np.pi/fi0)

    k_vectors.append(calculate_k_vector(z0, R, tita_max, fi0, n_leds, wavelength, 0 , 0))

    for m in range(0, max_steps, n_steps):
        for n in range(1, n_leds + 1):
            k_vector = calculate_k_vector(z0, R, tita_max, fi0, n_leds, wavelength,m ,n)
            k_vectors.append(k_vector)
    return k_vectors

def graph_support(k_vectors, NA):
    fig, ax = plt.subplots(1)
    radio = NA * np.linalg.norm(k_vectors[0])
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        ax.scatter(kx, ky, s=0.5, color="black")
        circle = plt.Circle((kx, ky), radio, alpha=0.2, linewidth=0.2)
        ax.set_aspect(1)
        ax.add_artist(circle)
    plt.show()

def create_circular_mask(h, w, center=None, radius=None):

    if center is None: # use the middle of the image
        center = (int(w/2), int(h/2))
    if radius is None: # use the smallest distance between the center and image walls
        radius = min(center[0], center[1], w-center[0], h-center[1])

    Y, X = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((X - center[0] - int(w/2))**2 + (Y-center[1] - int(h/2))**2)

    mask = dist_from_center <= radius
    return mask

def overlap(k_vectors, NA, pix_per_radius=100, shape=(1000,1000)):
    radius = NA * np.linalg.norm(k_vectors[0])
    px_size = radius/pix_per_radius
    img = np.zeros(shape=shape)
    shapex, shapey = shape
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        msk = create_circular_mask(shapex, shapey, center=(kx, ky), radius=radius)
        img[msk] = img[msk] + 1
    plt.imshow(img)
    plt.show()

def graph_led_positions(k_vectors, z0, R, tita_max, fi0, n_leds, n_steps, vector_length = 20):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    max_steps = int(2*np.pi/fi0)
    i = 0
    k0 = np.linalg.norm(k_vectors[0])
    for m in range(0, max_steps, n_steps):
        for n in range(1, n_leds + 1):
            x, y, z = calculate_positions(z0, R, tita_max, fi0, n_leds, m, n)
            ax.scatter(x, y, z)
            kx, ky, kz = vector_length* k_vectors[i+1]/k0
            ax.quiver(x,y,z,kx,ky,kz)
            i = i+1

    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([-250, -50])
    plt.show()
        
z0 = 0
R = 100
tita_max = np.pi/3
fi0 = 2*np.pi/64
n_leds = 5  
wavelength = 0.01
NA = 0.1
n_steps = 1


k_vectors = calculate_k_vectors(z0, R, tita_max, fi0, n_leds, n_steps, wavelength)
graph_led_positions(k_vectors, z0, R, tita_max, fi0, n_leds, n_steps)

graph_support(k_vectors, NA)

#erres = np.arange()
n_samples = 1000
overlap(k_vectors, NA, shape=(1000,1000))


