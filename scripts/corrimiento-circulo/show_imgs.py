import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

p = Path(".")
leds = ["07", "08", "09", "10", "11", "12", "13", "14", "15", "16", "17"]


fig, axs = plt.subplots(2, 5, figsize=(20, 10))
plt.tight_layout()

axs = np.array(axs).flatten()

for led, ax in zip(leds, axs):
    img = np.load(p/f"corrimiento-circulo/imagenes/18_{led}.npy")

    title = int(led) * 6 - 16*6
    ax.set_title("dist led x = "+str(title))
    ax.set_yticks([])
    ax.imshow(img, cmap="gray")

plt.show()
