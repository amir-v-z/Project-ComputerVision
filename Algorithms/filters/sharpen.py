import cv2
import numpy as np

# Light Sharpen
def sharpen_light(img):

    kernel = np.array([
        [0, -1,  0],
        [-1, 5, -1],
        [0, -1,  0]
    ])

    return cv2.filter2D(img, -1, kernel)

# Strong Sharpen
def sharpen_strong(img):

    kernel = np.array([
        [-1, -1, -1],
        [-1,  9, -1],
        [-1, -1, -1]
    ])

    return cv2.filter2D(img, -1, kernel)

# Very Strong Sharpen
def sharpen_very_strong(img):

    kernel = np.array([
        [-1, -1, -1],
        [-1, 13, -1],
        [-1, -1, -1]
    ])

    return cv2.filter2D(img, -1, kernel)