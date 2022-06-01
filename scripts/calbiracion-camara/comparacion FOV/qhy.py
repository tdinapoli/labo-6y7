import matplotlib.pylab as plt
# import lantz.drivers
from sys import path
path.append("home/chanoscopio/git/gigapixel/gigapixel/drivers/")
print(path)
from camera import QhyCamera as QHY

qhy = QHY()
qhy.exposure = 10000
qhy.gain = 20
qhy.offset = 20
qhy.binning = 1
out = qhy.get_frame()
qhy.close()
plt.imshow(out, cmap = 'gray')
plt.show()
