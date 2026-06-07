import cv2
import numpy as np

# پیاده‌سازی الگوریتم میانه
# Manual
def median_filter_manual(image, window_size=3):
    if window_size % 2 == 0:
        raise ValueError("Kernel size must be odd")

    height, width, channels = image.shape
    output = np.zeros_like(image)

    edge = window_size // 2

    padded = np.pad(
        image,
        ((edge, edge), (edge, edge), (0, 0)),
        mode="edge"
    )

    for y in range(height):
        for x in range(width):
            for c in range(channels):

                window = []

                for fy in range(-edge, edge + 1):
                    for fx in range(-edge, edge + 1):

                        pixel = padded[
                            y + edge + fy,
                            x + edge + fx,
                            c
                        ]

                        window.append(pixel)

                window.sort()

                output[y, x, c] = window[len(window)//2]

    return output

# OpenCV
def median_filter_opencv(image, kernel_size):
    return cv2.medianBlur(image, kernel_size)