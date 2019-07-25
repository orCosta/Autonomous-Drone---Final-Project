import numpy as np
import matplotlib.pyplot as plt
import cv2

# img1 = cv2.imread('t1.jpg')
# img2 = cv2.imread('t2.jpg')
# img3 = cv2.imread('t3.jpg')
# stitcher = cv2.createStitcher(False)
# res = stitcher.stitch((img1, img2, img3))

# img1 = cv2.imread('b1.jpg')
img2 = cv2.imread('b6.jpg')
img3 = cv2.imread('b7.jpg')
img4 = cv2.imread('b8.jpg')
img5 = cv2.imread('b2.jpg')
img6 = cv2.imread('b3.jpg')
img7 = cv2.imread('b4.jpg')
# img8 = cv2.imread('b8.jpg')

img5[550:,:] = 0
img6[550:,:] = 0
img7[550:,:] = 0
plt.imshow(img5)
plt.show()


images = [ img2, img3, img4]
stitcher = cv2.createStitcher(False)
result = stitcher.stitch(images)
# idx = np.argwhere(result[1]== -1)[0]
# plt.imshow(idx, cmap='gray')
# plt.show()

cv2.imwrite("./res_home.jpg", result[1])
map = result[1]
plt.imshow(map)
plt.show()
