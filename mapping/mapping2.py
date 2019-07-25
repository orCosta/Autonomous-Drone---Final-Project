import numpy as np
import matplotlib.pyplot as plt
import cv2

# img1 = cv2.imread('t1.jpg')
# img2 = cv2.imread('t2.jpg')
# img3 = cv2.imread('t3.jpg')
# stitcher = cv2.createStitcher(False)
# res = stitcher.stitch((img1, img2, img3))

img1 = cv2.imread('t1.jpg')
img2 = cv2.imread('t2.jpg')
img3 = cv2.imread('t3.jpg')

h, w, d = np.shape(img1)

img1[h//2, w//2, :] = 0
img2[h//2, w//2, :] = 0
img3[h//2, w//2, :] = 0
plt.imshow(img1)
plt.show()
# img4 = cv2.imread('t4.jpg')
# img5 = cv2.imread('t5.jpg')
images = [img1, img2, img3]
stitcher = cv2.createStitcher(False)
result = stitcher.stitch(images)
# idx = np.argwhere(result[1]== -1)[0]
# plt.imshow(idx, cmap='gray')
# plt.show()

cv2.imwrite("./res.jpg", result[1])
map = result[1]
plt.imshow(map)
plt.show()
