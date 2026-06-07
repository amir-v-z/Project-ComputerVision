import cv2
import numpy as np

# پیاده‌سازی الگوریتم میانگین
def average_filter(img, kernel_size=3):

    if kernel_size <= 1:
        raise ValueError("Kernel size must be greater than 1")

    kernel = np.ones((kernel_size, kernel_size), np.float32) / (kernel_size * kernel_size)

    return cv2.filter2D(img, -1, kernel)