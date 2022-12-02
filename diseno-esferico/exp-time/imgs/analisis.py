import numpy as np
import matplotlib.pyplot as plt
from dask_checkpoint import Storage, task

storage = Storage.from_fsspec("dask_cache")

t_exp = [7000, 8000, 18000, 300000, 2000000, 5000000, 5000000]
leds = [2, 3, 4, 5, 6, 7, 10]

@task(save=True)
def histograma(im, **kwargs):
    return np.histogram(im, **kwargs)

with storage():
    for led, t, in zip(leds, t_exp ):
        im = np.load(f"{led}_{t}.npy")
        counts, bins = histograma(im, bins=4096, range=(0, 4096)).compute()
        plt.stairs(counts, bins)
        plt.title(str(led))
        plt.figure()
        plt.imshow(im, cmap="gray")
        #plt.hist(bins[:-1], bins, weight=counts)
        plt.show()
        np.save(f"histogramas/{led}_{t}", counts)
        

    im = np.load("100000_HP.npy")
    counts, bins = histograma(im, bins=4096, range=(0, 4096)).compute()
    np.save(f"histogramas/{led}_{t}", counts)
    np.save(f"histogramas/bins", bins)
    plt.stairs(counts, bins)
    plt.figure()
    plt.imshow(im, cmap="gray")
    plt.show()
