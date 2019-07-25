import numpy as np
from matplotlib import pyplot as plt
import cv2
from scipy import signal

from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
# import matplotlib.pyplot as plt
# import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


# ##### INPUTS #########################################
size = 120
samp = [10, 10, 10, 7, 3, 20, 10, 10, 15, 3, 15, 10, 10, 12, 3, 10, 10,10, 12, 3]
num_samp_per_row = 5
num_rows = 4
s = np.array(samp).reshape((num_rows, num_samp_per_row))
x_start = 40
y_start = 30
########################################################

a = np.zeros((size, size))
s = np.flip(s, axis=0)

w = size-(2 * x_start)
h = size-(2 * y_start)
y_step = h//(num_rows -1)
x_step = w//(num_samp_per_row -1)
for i in range(num_rows):
    for j in range(num_samp_per_row-1):
        l = np.linspace(s[i, j], s[i, j+1], x_step)
        a[y_start + (i * y_step), x_start + (j * x_step):x_start + ((j+1) * x_step)] = l


for i in range(num_rows-1):
    for j in range(w):
        l=np.linspace(a[y_start + (i * y_step), x_start+j], a[y_start + ((i+1)* y_step), x_start+j], y_step)
        a[y_start + (i * y_step): y_start + ((i+1)* y_step), x_start+j] = l


plt.imshow(a, cmap='hot')
plt.show()

# **********************************************************************
# *************************** 3D PLOT **********************************
# **********************************************************************
a = a.T
nrows, ncols = a.shape
x = np.linspace(0, 120, ncols)
y = np.linspace(0, 120, nrows)
x, y = np.meshgrid(x, y)

region = np.s_[40:80, 30:90]
x, y, a = x[region], y[region], a[region]

# Set up plot
fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))

ls = LightSource(270, 45)
# To use a custom hillshading mode, override the built-in shading and pass
# in the rgb colors of the shaded surface calculated from "shade".
rgb = ls.shade(a, cmap=cm.gist_earth, vert_exag=0.1, blend_mode='soft')
surf = ax.plot_surface(x, y, a, rstride=1, cstride=1, facecolors=rgb,
                       linewidth=0, antialiased=False, shade=False)

plt.show()

