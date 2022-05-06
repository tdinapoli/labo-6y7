import numpay as np
import matplotlib.pyplot as plt

means = np.load("means")
stds = np.load('stds')
exp_times = np.load('')

for i in range(50):
    plt.errorbar(exp_times[i, :], means[i, :], yerr = stds[i, :], fmt = 'o', color = 'k')
    plt.show()
