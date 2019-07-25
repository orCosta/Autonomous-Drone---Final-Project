import json
import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from datetime import datetime


# ================================================================
# ========================  Globals ==============================
# ================================================================
IM_PATH = "dump/"
LOGS_PATH = "dump/logs.json"
IM_PREFIX = "im_"
FORMAT = ".jpg"
REG_MAP = "map"
# ================================================================
# =========================  DEBUG ===============================
# ================================================================

def add_heights_stamp_to_map(map1, heights_list, im_list):
    im1 = np.copy(map1)
    im2 = np.copy(map1)

    for i, im in enumerate(im_list):
        temp_i = cv.imread(IM_PATH+im, 0)
        p = _find_pos(temp_i, im1, patch_size=650)
        font = cv.FONT_HERSHEY_SIMPLEX
        cv.putText(im1, "*" + str(heights_list[i]), p, font, 1, (0, 0, 255), 2, cv.LINE_AA)
        cv.putText(im2, "*" + str(i+1), p, font, 1, (0, 0, 255), 2, cv.LINE_AA)

    filename1 = "text_h_map.jpg"
    filename2 = "text_idx_map.jpg"
    cv.imwrite(IM_PATH + filename1, im1)
    cv.imwrite(IM_PATH + filename2, im2)

# ================================================================
# ================  Auxiliary functions ==========================
# ================================================================


def _read_logs():
    '''
    Reads parse and returns the flight logs.
    :return: heights matrix aligned with the map, and the images name list.
    '''
    with open(LOGS_PATH, 'r') as fp:
        data = json.load(fp)

    num_rows = data['num_rows']
    row_size = data['row_size']
    num_im = int(data["num_imgs"])
    h = data['heights']
    samples = []
    for k in sorted(h):
        samples.append(h[k])
        if len(samples) == num_im:
            break

    heights_matix = np.array(samples).reshape((num_rows, row_size))    #TODO: check the order of the matrix
    for i in range(num_rows):
        if not i % 2:
            heights_matix[i] = np.flip(heights_matix[i])

    im_name_list = []
    for i in range(1, num_im+1):
        im_name_list.append(IM_PREFIX + str(i) + FORMAT)

    return samples, heights_matix, num_rows, row_size, im_name_list


def _stitch_images_to_map(image_list):                                    #TODO : check option for image filtering
    '''
    Use cv2 stitcher to stitch the images to one map and save the result.
    Using mode=SCAN.
    :param image_list: list of images names. the order is not important.
    '''
    imgs = []
    for img_name in image_list:
        img = cv.imread(IM_PATH + img_name)
        if img is None:
            print("can't read image " + img_name)
        imgs.append(img)

    stitcher = cv.Stitcher.create(mode=1)
    status, map = stitcher.stitch(imgs)

    if status != cv.Stitcher_OK:
        print("Can't stitch images, error code = %d" % status)
        return
    cv.imwrite(IM_PATH + REG_MAP + FORMAT, map)
    print("stitching completed successfully.")
    return map


def _find_pos(img, main_img, patch_size=200):
    '''
    Finds the position of the given image inside the main image and returns the coordinates in the main image.
    Using normalized cross correlation technique.
    :param img: the template to find in the main image.
    :param main_img:
    :param patch_size: the amount of pixels to use for the matching method, depend in the size of the main image.
    :return: x,y position of img center in main_img
    '''
    h, w = np.shape(img)
    y1 = int(h/2) - int(patch_size/2)
    y2 = int(h/2) + int(patch_size/2)
    x1 = int(w/2) - int(patch_size/2)
    x2 = int(w/2) + int(patch_size/2)

    center = img[y1:y2, x1:x2]
    # plt.imshow(center, cmap='gray')
    # plt.show()
    method = cv.TM_CCOEFF_NORMED
    img_t = main_img.copy()
    res = cv.matchTemplate(img_t, center, method)
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

    return (max_loc[0] + patch_size//2, max_loc[1] + patch_size//2)


def add_heat_map_layer(img, heights, start_pos, v_step, h_step, filename):   #TODO: save layer2 in separate file for the 3D model
    '''
    Takes the given heights matrix and add it to the map as colored heat layer.
    The position of the measurements determined by the given start pos and the intervals.
    Between the measurements linear adjustment is performed to fill the gaps.
    :param img: the map. (Gray scale)
    :param heights: heights matrix s.t the heights are in the same order as they appears on the real map.
    :param start_pos: the top left corner position.
    :param v_step: horizontal interval.
    :param h_step: vertical interval.
    :param filename: the name of the result map.
    '''
    x_start, y_start = start_pos
    n_rows, n_cols = heights.shape
    layer1 = img

    layer2 = np.zeros((layer1.shape[0], layer1.shape[1]))

    for i in range(n_rows):
        for j in range(n_cols-1):
            l = np.linspace(heights[i, j], heights[i, j+1], h_step)
            layer2[y_start + (i * v_step), x_start + (j * h_step):x_start + ((j + 1) * h_step)] = l

    for i in range(n_rows-1):
        for j in range(h_step*(n_cols-1)):
            l=np.linspace(layer2[y_start + (i * v_step), x_start + j], layer2[y_start + ((i + 1) * v_step), x_start + j], v_step)
            layer2[y_start + (i * v_step): y_start + ((i + 1) * v_step), x_start + j] = l

    extent = 0, layer1.shape[1], 0, layer1.shape[0]
    fig, axs = plt.subplots(1, 1)
    im1 = axs.imshow(layer1, cmap=plt.cm.gray, interpolation='nearest', extent=extent)
    im2 = axs.imshow(layer2, cmap=plt.cm.viridis, alpha=.3, interpolation='bilinear', extent=extent)
    fig.colorbar(im2,orientation='vertical', fraction=.1)
    plt.savefig(IM_PATH + filename + FORMAT, format='jpg', dpi=1000)
    plt.show()


def _find_heights_matrix_coordinates(map1, first_row_im, last_row_im, row_size, num_rows):
    '''
    Finds the spreading of the heights matrix over the map.
    Finds the start position (top left) and the intervals between the measurements in x and y axis.
    the position based on the average distance between the images as the appears in the map.
    :param map1: the image of the map. (Gray scale)
    :param first_row_im: list of images names - that fit to the upper part of the map.
    :param last_row_im: list of images names - that fit to the bottom part of the map.
    :param row_size: the number of images in each row.
    :param num_rows: the number of total rows of the original images matrix.
    :return: top left position(start point), horizontal step, vertical step
    '''
    x_steps = []
    upper_line_y_pos = []
    bottom_line_y_pos = []
    p_size = 650
    for i in range(row_size-1):
        # First row
        img1 = cv.imread(IM_PATH + first_row_im[i], 0)
        img2 = cv.imread(IM_PATH + first_row_im[i + 1], 0)
        p1 = _find_pos(img1, map1, patch_size=p_size)
        p2 = _find_pos(img2, map1, patch_size=p_size)
        x_steps.append(np.abs(p1[0] - p2[0]))
        upper_line_y_pos.append(p1[1])

        # Last row
        img1 = cv.imread(IM_PATH + last_row_im[i], 0)
        img2 = cv.imread(IM_PATH + last_row_im[i + 1], 0)
        p1 = _find_pos(img1, map1, patch_size=p_size)
        p2 = _find_pos(img2, map1, patch_size=p_size)
        x_steps.append(np.abs(p1[0] - p2[0]))
        bottom_line_y_pos.append(p1[1])

    h_step = int(np.mean(x_steps))
    v_step = int(np.abs(np.mean(upper_line_y_pos) - np.mean(bottom_line_y_pos)) // (num_rows - 1))

    c_im = cv.imread(IM_PATH + first_row_im[-1], 0)                             #TODO : change to 0 if we change the order
    top_left = _find_pos(c_im, map1, patch_size=p_size)
    return top_left, h_step, v_step


# ================================================================
# =========================== Classes  ===========================
# ================================================================

# ================================================================
# =========================== Main ===============================
# ================================================================

def create_map():
    print("step #1")
    h_list, heights_matix, num_rows, row_size, im_name_list = _read_logs()

    # layer1 = _stitch_images_to_map(im_name_list)
    # layer1 = cv.cvtColor(layer1, cv.COLOR_BGR2GRAY)
    layer1 = cv.imread(IM_PATH + REG_MAP + FORMAT, 0)
    add_heights_stamp_to_map(layer1, h_list, im_name_list)
    print("step #2")
    #find heights pos:
    top_left, h_step, v_step = _find_heights_matrix_coordinates(layer1, im_name_list[:row_size], im_name_list[-row_size:], row_size, num_rows)
    add_heat_map_layer(layer1, heights_matix, top_left, v_step, h_step, 'heat_map')

    # print(top_left)
    # print(h_step)
    # print(v_step)
    # plt.imshow(layer1)
    # plt.show()

if __name__ == '__main__':
    # create_map()
    im_list = ["im_1.jpg","im_2.jpg","im_3.jpg","im_4.jpg","im_5.jpg","im_6.jpg","im_7.jpg","im_8.jpg","im_9.jpg","im_10.jpg","im_11.jpg","im_12.jpg","im_13.jpg","im_14.jpg","im_15.jpg","im_16.jpg","im_17.jpg","im_18.jpg","im_19.jpg","im_20.jpg","im_21.jpg","im_22.jpg","im_23.jpg","im_24.jpg","im_25.jpg","im_26.jpg","im_27.jpg","im_28.jpg","im_29.jpg","im_30.jpg","im_31.jpg","im_32.jpg"]
    im_list = ["im_3.jpg", "im_6.jpg", "im_7.jpg", "im_11.jpg", "im_14.jpg"]

    _stitch_images_to_map(im_list)


