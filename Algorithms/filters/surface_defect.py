import numpy as np
import cv2

# پیاده‌سازی الگوریتم تشخیص ضایعه سطحی
def surface_defect_detection(image, element_size=5, threshold=100, mode="counting"):
    
    # تبدیل به خاکستری برای پردازش
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    else:
        gray = image

    h, w = gray.shape

    # تصویر خروجی سیاه است و نقاط ضایعه سفید می‌شوند
    output = np.zeros((h, w), dtype=np.uint8)
    defect_found = False

    # n*n پیمایش تصویر به صورت بلوک‌های => (Element Size)
    for y in range(0, h - element_size, element_size):
        for x in range(0, w - element_size, element_size):
            
            # المنت فعلی
            e1 = gray[y:y+element_size, x:x+element_size]
            e_neighbor = gray[y:y+element_size, x+element_size:x+2*element_size]

            # بررسی اینکه همسایه از کادر تصویر خارج نشود
            if e_neighbor.shape != e1.shape:
                continue

            # روش Area Counting:
            # اختلاف پیکسل به پیکسل در المنت‌ها
            if mode == "counting":
                diff = np.abs(e1.astype(np.int16) - e_neighbor.astype(np.int16))
                if np.any(diff > threshold):
                    output[y:y+element_size, x:x+element_size] = 255
                    defect_found = True

            # روش Area Averaging:
            # اختلاف میانگین المنت‌ها
            elif mode == "averaging":
                avg1 = np.mean(e1)
                avg2 = np.mean(e_neighbor)
                
                if abs(avg1 - avg2) > threshold:
                    output[y:y+element_size, x:x+element_size] = 255
                    defect_found = True

    return output, defect_found