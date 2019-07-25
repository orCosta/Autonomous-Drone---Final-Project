import numpy as np
import matplotlib.pyplot as plt
import cv2

# A way to find the first LiDar sample on the final map.
# Using CC with a patch of the center of the first image.


img1 = cv2.imread('t1.jpg', 0)
pan_img = cv2.imread('res1.jpg', 0)
plt.imshow(img1, cmap='gray')
plt.show()
h, w = np.shape(img1)
patch_size = 120
y1 = int(h/2) - int(patch_size/2)
y2 = int(h/2) + int(patch_size/2)
x1 = int(w/2) - int(patch_size/2)
x2 = int(w/2) + int(patch_size/2)
center = img1[y1:y2, x1:x2]

plt.imshow(center, cmap='gray')
plt.show()

m = 'cv2.TM_CCOEFF_NORMED'
method = eval(m)
img_t = pan_img.copy()
res = cv2.matchTemplate(img_t, center, method)
a1 = np.argwhere(res == np.max(res))
res2 = res > 0.85
idx = np.argwhere(res2)[0]

plt.imshow(pan_img, cmap='gray')
plt.imshow(res2, cmap='gray')
plt.show()




print("test1")
