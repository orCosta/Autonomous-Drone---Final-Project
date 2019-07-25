## https://matplotlib.org/api/_as_gen/matplotlib.pyplot.imshow.html

import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.colors import LightSource
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import


s = np.array([[10, 10, 5, 3], [5, 5, 5, 0]])

# fig = plt.figure(frameon=False)

temp = cv2.imread('res.jpg', 0)
Z1 = temp[:500, :]

# plt.imshow(Z1)
# plt.show()

Z2 = np.zeros((Z1.shape[0], Z1.shape[1]))

y_step = 200
x_step = 300
y_start = 200
x_start = 100

for i in range(2):
    for j in range(3):
        l = np.linspace(s[i, j], s[i, j+1], x_step)
        Z2[y_start + (i * y_step), x_start + (j * x_step):x_start + ((j+1) * x_step)] = l


for i in range(1):
    for j in range(900):
        l=np.linspace(Z2[y_start + (i * y_step), x_start+j], Z2[y_start + ((i+1)* y_step), x_start+j], y_step)
        Z2[y_start + (i * y_step): y_start + ((i+1)* y_step), x_start+j] = l



extent = 0, Z1.shape[1], 0, Z1.shape[0]
fig, axs = plt.subplots(1, 1)
im1 = axs.imshow(Z1, cmap=plt.cm.gray, interpolation='nearest', extent=extent)
im2 = axs.imshow(Z2, cmap=plt.cm.viridis, alpha=.3, interpolation='bilinear', extent=extent)
# im3 = axs[2].imshow(Z1, cmap=plt.cm.gray, interpolation='nearest', extent=extent)
# im4 = axs[2].imshow(Z2, cmap=plt.cm.viridis, alpha=.3, interpolation='bilinear', extent=extent)
# im1 = plt.imshow(Z1, cmap=plt.cm.gray, interpolation='nearest', extent=extent)
# im2 = plt.imshow(Z2, cmap=plt.cm.viridis, alpha=.3, interpolation='bilinear', extent=extent)
fig.colorbar(im2,orientation='vertical', fraction=.1)

plt.show()

# **********************************************************************
# *************************** 3D PLOT **********************************
# **********************************************************************
# Z3 = Z2.T
# Z2 = res = cv2.resize(Z3, dsize=(200, 50), interpolation=cv2.INTER_CUBIC)
# plt.imshow(Z2)
# plt.show()
# nrows, ncols = Z2.shape
# x = np.linspace(0, 120, ncols)
# y = np.linspace(0, 120, nrows)
# x, y = np.meshgrid(x, y)
#
# region = np.s_[5:35, 80:160]
# x, y, Z2 = x[region], y[region], Z2[region]
#
# # Set up plot
# fig, ax = plt.subplots(subplot_kw=dict(projection='3d'))
#
# ls = LightSource(300, 50)
# # To use a custom hillshading mode, override the built-in shading and pass
# # in the rgb colors of the shaded surface calculated from "shade".
# rgb = ls.shade(Z2, cmap=cm.viridis, vert_exag=0.1, blend_mode='soft')
# surf = ax.plot_surface(x, y, Z2, rstride=1, cstride=1, facecolors=rgb,
#                        linewidth=0, antialiased=False, shade=False)
#
# plt.show()