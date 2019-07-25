## https://mono.software/2018/03/14/Image-stitching/


import os
import sys
import cv2
import math
import numpy as np
from matplotlib import pyplot as plt
from numpy import linalg


def findDimensions(image, homography):
    base_p1 = np.ones(3, np.float32)
    base_p2 = np.ones(3, np.float32)
    base_p3 = np.ones(3, np.float32)
    base_p4 = np.ones(3, np.float32)

    (y, x) = image.shape[:2]

    base_p1[:2] = [0, 0]
    base_p2[:2] = [x, 0]
    base_p3[:2] = [0, y]
    base_p4[:2] = [x, y]

    max_x = None
    max_y = None
    min_x = None
    min_y = None

    for pt in [base_p1, base_p2, base_p3, base_p4]:

        hp = np.matrix(homography, np.float32) * np.matrix(pt, np.float32).T

        hp_arr = np.array(hp, np.float32)

        normal_pt = np.array([hp_arr[0] / hp_arr[2], hp_arr[1] / hp_arr[2]], np.float32)

        if (max_x == None or normal_pt[0, 0] > max_x):
            max_x = normal_pt[0, 0]

        if (max_y == None or normal_pt[1, 0] > max_y):
            max_y = normal_pt[1, 0]

        if (min_x == None or normal_pt[0, 0] < min_x):
            min_x = normal_pt[0, 0]

        if (min_y == None or normal_pt[1, 0] < min_y):
            min_y = normal_pt[1, 0]

    min_x = min(0, min_x)
    min_y = min(0, min_y)

    return (min_x, min_y, max_x, max_y)


# ====================================================================================

def stitch_to_base(img1, img2):
    '''

    :param base_im:
    :param n_im:
    :return:
    '''
    # Read the base image
    base_img = cv2.GaussianBlur(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY), (5, 5), 0)
    # Read in the next image
    next_img = cv2.GaussianBlur(cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY), (5, 5), 0)

    # Use the SIFT feature detector
    detector = cv2.xfeatures2d.SIFT_create()
    # detector = cv2.ORB_create()


    # Find key points in base image for motion estimation
    base_features, base_descs = detector.detectAndCompute(base_img, None)
    # base_features, base_descs = cv2.ORB.detectAndCompute(base_img, None)

    # Parameters for nearest-neighbor matching
    FLANN_INDEX_KDTREE = 1
    flann_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    matcher = cv2.FlannBasedMatcher(flann_params, {})

    print("\t Finding points...")
    # Find points in the next frame
    next_features, next_descs = detector.detectAndCompute(next_img, None)
    # next_features, next_descs = cv2.ORB.detectAndCompute(next_img, None)
    matches = matcher.knnMatch(next_descs, trainDescriptors=base_descs, k=2)
    print("\t Match Count: {}".format(len(matches)))

    matches_subset = []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * 0.75:
            matches_subset.append(m[0])

    print("\t Filtered Match Count: {}".format(len(matches_subset)))
    distance = 0.0

    for match in matches_subset:
        distance += match.distance
    print("\t Distance from Key Image: {}".format(distance))

    averagePointDistance = distance / float(len(matches_subset))
    print("\t Average Distance: {}".format(averagePointDistance))

    kp1 = []
    kp2 = []

    for match in matches_subset:
        kp1.append(base_features[match.trainIdx])
        kp2.append(next_features[match.queryIdx])

    p1 = np.array([k.pt for k in kp1])
    p2 = np.array([k.pt for k in kp2])

    H, status = cv2.findHomography(p1, p2, cv2.RANSAC, 5.0)

    print("{0} / {1}  inliers/matched".format(np.sum(status), len(status)))

    H = H / H[2, 2]
    H_inv = linalg.inv(H)

    (min_x, min_y, max_x, max_y) = findDimensions(next_img, H_inv)

    # Adjust max_x and max_y by base img size
    max_x = max(max_x, base_img.shape[1])
    max_y = max(max_y, base_img.shape[0])

    move_h = np.matrix(np.identity(3), np.float32)

    if (min_x < 0):
        move_h[0, 2] += -min_x
        max_x += -min_x

    if (min_y < 0):
        move_h[1, 2] += -min_y
        max_y += -min_y

    mod_inv_h = move_h * H_inv

    img_w = int(math.ceil(max_x))
    img_h = int(math.ceil(max_y))

    print("New Dimensions: ", (img_w, img_h))

    # crop edges
    print("Cropping...")
    base_h, base_w = base_img.shape
    next_h, next_w = next_img.shape

    base_img_rgb = img1[5:(base_h - 5), 5:(base_w - 5)]
    next_img_rgb = img2[5:(next_h - 5), 5:(next_w - 5)]

    # Warp the new image given the homography from the old image
    base_img_warp = cv2.warpPerspective(base_img_rgb, move_h, (img_w, img_h))
    print("Warped base image")
    plt.imshow(base_img_warp)
    plt.show()


    next_img_warp = cv2.warpPerspective(next_img_rgb, mod_inv_h, (img_w, img_h))
    print("Warped next image")
    plt.imshow(next_img_warp)
    plt.show()

    # Put the base image on an enlarged palette
    enlarged_base_img = np.zeros((img_h, img_w, 3), np.uint8)

    (ret, data_map) = cv2.threshold(cv2.cvtColor(next_img_warp, cv2.COLOR_BGR2GRAY), 0, 255, cv2.THRESH_BINARY)

    # add base image
    enlarged_base_img = cv2.add(enlarged_base_img, base_img_warp, mask=np.bitwise_not(data_map), dtype=cv2.CV_8U)

    # add next image
    final_img = cv2.add(enlarged_base_img, next_img_warp, dtype=cv2.CV_8U)
    plt.imshow(final_img)
    plt.show()
    # Crop black edge
    final_gray = cv2.cvtColor(final_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(final_gray, 1, 255, cv2.THRESH_BINARY)
    dino, contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    max_area = 0
    best_rect = (0, 0, 0, 0)

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        deltaHeight = h - y
        deltaWidth = w - x

        area = deltaHeight * deltaWidth
        if (area > max_area and deltaHeight > 0 and deltaWidth > 0):
            max_area = area
            best_rect = (x, y, w, h)

    if (max_area > 0):
        final_img_crop = final_img[best_rect[1]:best_rect[1] + best_rect[3], best_rect[0]:best_rect[0] + best_rect[2]]

        final_img = final_img_crop
    # output
    final_filename = "dump/base_im.jpg"
    cv2.imwrite(final_filename, final_img)

# =============================================================================================

def stitch_together(img_name_lst):
    img1 = cv2.imread(img_name_lst[0])
    img2 = cv2.imread(img_name_lst[1])
    # plt.imshow(img1)
    # plt.show()
    # plt.imshow(img2)
    # plt.show()
    stitch_to_base(img1, img2)
    for i in range(2, len(img_name_lst)):
        img1 = cv2.imread('dump/base_im.jpg')
        img2 = cv2.imread(img_name_lst[i])
        # plt.imshow(img1)
        # plt.show()
        # plt.imshow(img2)
        # plt.show()
        stitch_to_base(img1, img2)


# images_list = ['map3/t32.jpg', 'map3/t31.jpg', 'map3/t30.jpg', 'map3/t15.jpg','map3/t14.jpg', 'map3/t13.jpg', 'map3/t12.jpg', 'map3/t11.jpg', 'map3/t10.jpg']
images_list = ['dump/im_5.jpg','dump/im_6.jpg', 'dump/im_7.jpg', 'dump/im_8.jpg']
stitch_together(images_list)
