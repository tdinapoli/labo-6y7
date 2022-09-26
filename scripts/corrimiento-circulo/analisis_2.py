import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import itertools

def mask(img, threshold):
    img[img < threshold] = 0
    img[img >= threshold] = 1
    return img

def get_max_arr(arr):
    mx = np.array(np.where(arr == 1))
    return np.max(mx[1,:])

def max_x(arr, threshold):
    arr = mask(arr, threshold)
    mx = get_max_arr(arr)
    return mx

def calc_kx(altura, ledx, NA, wlen):
    ledx = int(ledx)
    fi = np.arctan2(altura, 6*(ledx - 16))
    kx = NA * np.cos(fi)/wlen
    return kx

def max_px_to_mm(px_size, mx_px):
    return px_size * (mx_px - 9344/2)

def lineal(x, m, b):
    return m*x + b


p = Path("./imagenes-22-09-26")


datos = {}
NA = 0.1
wlen = 500e-6
for fname in p.iterdir():
    fname = str(fname.parts[1])
    data = fname[:-4].split("_")
    x, y, cm = data
    if cm not in datos.keys():
        datos[cm] = []

for key in datos.keys():
    fnames = p.glob(f"**/*{key}.npy")
    mx_px_mms = []
    kxs = []
    for fname in fnames:
        img = np.load(fname)
        fname = str(fname.parts[1])
        data = fname[:-4].split("_")
        x, y, cm = data
        altura = float(cm)*10

        mx_px = max_x(img, 1200)
        mx_px_mm = max_px_to_mm(3.2e-3, mx_px)

        kx = calc_kx(altura, x, NA, wlen)
        mx_px_mms.append(mx_px_mm)
        kxs.append(kx)

    plt.imshow(img)
    plt.show()
    kxs_norm = wlen * np.array(kxs)/NA
    mx_px_mms = np.array(mx_px_mms) + 0.5

    popt, pcov = curve_fit(lineal, kxs_norm, mx_px_mms)
    m, b = popt
    datos[key].append((m, b))
    plt.plot(kxs_norm, mx_px_mms, 'o')
    x_plot = np.linspace(np.min(kxs_norm), np.max(kxs_norm), 2)
    plt.plot(x_plot, lineal(x_plot, m, b))
    plt.title(f"{m}, {b}")
    plt.show()

    


