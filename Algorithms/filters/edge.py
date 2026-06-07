import numpy as np
import cv2

# پیاده‌سازی الگوریتم تشخیص لبه
# Manual
def edge_detection_manual(img, kernel, threshold=100):

    gray = np.mean(img, axis=2).astype(np.float32)

    H, W = gray.shape
    output = np.zeros((H, W), dtype=np.uint8)

    for i in range(1, H - 1):
        for j in range(1, W - 1):

            val = (
                gray[i-1, j-1] * kernel[0,0] +
                gray[i,   j-1] * kernel[1,0] +
                gray[i+1, j-1] * kernel[2,0] +

                gray[i-1, j]   * kernel[0,1] +
                gray[i,   j]   * kernel[1,1] +
                gray[i+1, j]   * kernel[2,1] +

                gray[i-1, j+1] * kernel[0,2] +
                gray[i,   j+1] * kernel[1,2] +
                gray[i+1, j+1] * kernel[2,2]
            )

            output[i, j] = 255 if val > threshold else 0

    return output

# OpenCV
def edge_detection_opencv(img, kernel, threshold=100):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    conv = cv2.filter2D(gray, -1, kernel)

    _, thresh = cv2.threshold(conv, threshold, 255, cv2.THRESH_BINARY)

    return thresh

# Sobel
def sobel_edge_detection(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # گرادیان افقی
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)

    # گرادیان عمودی
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    # اندازه گرادیان
    magnitude = cv2.magnitude(sobel_x, sobel_y)

    # uint8 تبدیل به
    magnitude = np.uint8(np.clip(magnitude, 0, 255))

    return magnitude

# LoG
def log_edge_detection(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gaussian Blur
    blur = cv2.GaussianBlur(gray, (3, 3), 0)

    # Laplacian
    laplacian = cv2.Laplacian(blur, cv2.CV_64F)

    result = np.uint8(np.absolute(laplacian))

    return result

# Canny
def canny_edge_detection(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 100, 200)

    return edges

# Default Kernel
default_edge_kernel = np.array([
    [-1,-1, 0],
    [-1, 0, 1],
    [ 0, 1, 1]
])