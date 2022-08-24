import numpy as np
import matplotlib.pyplot as plt

def calculate_position_sph(z0, R, tita_max, fi0, n_leds, m, n): # units in mm
    fim = m * fi0
    titan = np.pi - tita_max* n/n_leds
    x = R * np.cos(m*fi0) * np.sin(titan)
    y = R * np.sin(m*fi0) * np.sin(titan)
    z = -z0 + R*np.cos(titan)
    return (x, y, z)

def calculate_positions_sph(*args):
    max_steps = int(2*np.pi/fi0)
    positions = []
    for m in range(0, max_steps, n_steps):
        for n in range(1, n_leds + 1):
            positions.append(calculate_position_sph(z0, R, tita_max, fi0, n_leds, m, n))
    return positions
            

def calculate_k_vector_general(led_position, wavelength):
    x, y, z = led_position
    #k_0 = 2*np.pi/wavelength
    k_0 = 1/wavelength
    module = np.linalg.norm(np.array([x,y,z]))
    kx = -x/module
    ky = -y/module
    kz = -z/module
    k_vector = np.array([kx,ky,kz])*k_0
    return k_vector

def calculate_k_vector_sph(z0, R, tita_max, fi0, n_leds, wavelength,m ,n):
    x, y, z = calculate_position_sph(z0, R, tita_max, fi0, n_leds, m, n)
    k_0 = 2*np.pi/wavelength
    module = np.linalg.norm(np.array([x,y,z]))
    kx = -x/module
    ky = -y/module
    kz = -z/module
    k_vector = np.array([kx,ky,kz])*k_0
    return k_vector

def calculate_k_vectors_sph(z0, R, tita_max, fi0, n_leds, n_steps, wavelength):
    k_vectors = []
    max_steps = int(2*np.pi/fi0)

    pos_0 = calculate_position_sph(z0, R, tita_max, fi0, n_leds, 0, 0)
    k_vectors.append(calculate_k_vector_general(pos_0, wavelength))

    for m in range(0, max_steps, n_steps):
        for n in range(1, n_leds + 1):
            led_pos = calculate_position_sph(z0, R, tita_max, fi0, n_leds, m, n)
            k_vectors.append(calculate_k_vector_general(led_pos, wavelength))
    return k_vectors

def calculate_position_matrix(z0, dx, dy, i, j, led_0_0_offset=(0,0)):
    x, y = j*dx + led_0_0_offset[0], i*dy + led_0_0_offset[1]
    z = -z0
    return (x, y, z)

def calculate_k_vector_matrix(z0, dx, dy, wavelength, i, j, led_0_0_offset=(0,0)):
    x, y, z = calculate_position_matrix(z0, dx, dy, i, j, led_0_0_offset=led_0_0_offset)
    k_0 = 2*np.pi/wavelength
    module = np.linalg.norm(np.array([x,y,z]))
    kx = -x/module
    ky = -y/module
    kz = -z/module
    k_vector = np.array([kx, ky, kz])*k_0
    return k_vector

def calculate_k_vectors_matrix(z0, dx, dy, wavelength, x_range=range(-2, 3, 1), y_range=range(-2, 3, 1) ,led_0_0_offset=(0,0)):
    k_vectors = []
    for i in x_range:
        for j in y_range:
            led_pos = calculate_position_matrix(z0, dx, dy, i, j, led_0_0_offset=led_0_0_offset)
            k_vector = calculate_k_vector_general(led_pos, wavelength)
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
    ax.set_title("wavelength="+str(wavelength))
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
    img = np.zeros(shape=shape)
    shapex, shapey = shape
    for k_vector in k_vectors:
        kx, ky, kz = k_vector
        msk = create_circular_mask(shapex, shapey, center=(kx, ky), radius=radius)
        img[msk] = img[msk] + 1
    ax.imshow(img)
    ax.set_title("wavelength="+str(wavelength)+"m\nfreq_per_pix="+str(freq_per_pix)+"$m^{-1}$"+"\n n_fotos="+str(len(k_vectors)))
    return img

#def graph_led_positions(calculate_pos_func, fig, **kwargs):
#    print(vector_length, z0, R, tita_max, fi0, n_leds, n_steps)
#    ax = fig.add_subplot(projection='3d')
#    positions = calculate_pos_func(**kwargs)
#    k_0 = np.linalg.norm(calculate_k_vector_general(positions[0], wavelength))
#    for position in positions:
#        x, y, z = position
#        ax.scatter(x,y,z)
#        kx, ky, kz = vector_length * calculate_k_vector_general(position, wavelength)/k_0
#        ax.quiver(x,y,z,kx,ky,kz)
#    plt.show()


def graph_led_positions_sph(k_vectors, z0, R, tita_max, fi0, n_leds, n_steps, ax, vector_length = 20):
    max_steps = int(2*np.pi/fi0)
    i = 0
    k0 = np.linalg.norm(k_vectors[0])
    for m in range(0, max_steps, n_steps):
        for n in range(1, n_leds + 1):
            x, y, z = calculate_position_sph(z0, R, tita_max, fi0, n_leds, m, n)
            ax.scatter(x, y, z, color="tab:brown")
            kx, ky, kz = vector_length* k_vectors[i+1]/k0
            ax.quiver(x,y,z,kx,ky,kz, linewidth=1,color="tab:olive")
            i = i+1


def graph_led_positions_matrix(k_vectors, z0, dx, dy, ax, range_x=range(-2, 3, 1), range_y=range(-2, 3,1), vector_length=20):
    k_0 = np.linalg.norm(k_vectors[0])
    ii = 0
    for i in range_x:
        for j in range_y:
            x, y, z = calculate_position_matrix(z0, dx, dy, i, j, led_0_0_offset=(0,0))
            ax.scatter(x,y,z, color="tab:orange")
            kx, ky, kz = vector_length * k_vectors[ii]/k_0
            ax.quiver(x, y, z, kx, ky, kz, linewidth=1,color="tab:blue")
            ii = ii + 1


        
z0 = 0
R = 100
tita_max = np.pi/4
fi0 = 2*np.pi/30
n_leds = 6
wavelength = 500e-9
NA = 0.1
n_steps = 1

z0_matrix = 100
dx = 6
dy = 6
range_x = range(-10, 11, 1)
range_y = range(-10, 11, 1)

vector_length=10
freq_per_pix=4e3

k_vectors_sph = calculate_k_vectors_sph(z0, R, tita_max, fi0, n_leds, n_steps, wavelength)

#fig = plt.figure()
#ax = fig.add_subplot(projection='3d')
#ax.set_xlim([-100, 100])
#ax.set_ylim([-100, 100])
#ax.set_zlim([-250, -50])
#ax.scatter(0,0,0, color="k", s=30)
#
#graph_led_positions_sph(k_vectors_sph, z0, R, tita_max, fi0, n_leds, n_steps, ax)
#plt.show()
#
#fig = plt.figure()
#ax = fig.add_subplot(projection='3d')
#ax.set_xlim([-100, 100])
#ax.set_ylim([-100, 100])
#ax.set_zlim([-250, -50])
#
k_vectors_matrix = calculate_k_vectors_matrix(z0_matrix, dx, dy, wavelength, x_range=range_x, y_range=range_y) 
#
#graph_led_positions_matrix(k_vectors_matrix, z0_matrix, dx, dy, ax, range_x = range_x, range_y=range_y)
#
#plt.show()
#
#
#graph_support(k_vectors_sph, NA)
#graph_support(k_vectors_matrix, NA)
#plt.show()

#erres = np.arange()
n_samples = 1000
overlap(k_vectors_sph, NA, freq_per_pix=freq_per_pix, shape=(1000,1000))
overlap(k_vectors_matrix, NA, freq_per_pix=freq_per_pix, shape=(1000,1000))
plt.show()


