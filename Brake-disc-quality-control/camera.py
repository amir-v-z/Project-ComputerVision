import os
import sys
import cv2
import subprocess

# آدرس ویدئوی DroidCam
STREAM_URL = "http://192.168.1.2:4747/video"

# مسیر پوشه پروژه
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ورودی مورد انتظار برنامه اصلی
IMG_DIR = os.path.join(BASE_DIR, "img")
SAVE_PATH = os.path.join(IMG_DIR, "disc.jpg")

# فایل اصلی تحلیل
QC_SCRIPT = os.path.join(BASE_DIR, "brake_disc_qc.py")

# اطمینان از وجود پوشه img
os.makedirs(IMG_DIR, exist_ok=True)

# باز کردن استریم DroidCam
cap = cv2.VideoCapture(STREAM_URL)

if not cap.isOpened():
    raise RuntimeError(
        "DroidCam stream could not be opened.\n"
        "IP address, port and Wi-Fi connection را بررسی کنید."
    )

print("s = save image and analyze | q = quit")

while True:
    ok, frame = cap.read()

    if not ok or frame is None:
        print("Frame could not be received.")
        break

    preview = frame.copy()

    cv2.putText(
        preview,
        "S: Save and Analyze   Q: Quit",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.imshow("Brake Disc Camera", preview)

    key = cv2.waitKey(1) & 0xFF

    # ذخیره تصویر و اجرای تحلیل
    if key == ord("s"):
        saved = cv2.imwrite(SAVE_PATH, frame)

        if not saved:
            print(f"Could not save image: {SAVE_PATH}")
            continue

        print(f"Image saved: {SAVE_PATH}")
        print("Starting brake disc quality control...")

        # بستن دوربین قبل از اجرای تحلیل
        cap.release()
        cv2.destroyAllWindows()

        # اجرای brake_disc_qc.py با همان Python فعلی
        result = subprocess.run(
            [sys.executable, QC_SCRIPT],
            cwd=BASE_DIR
        )

        if result.returncode == 0:
            print("Analysis finished successfully.")
        else:
            print(
                f"Analysis failed with return code: "
                f"{result.returncode}"
            )

        break

    # خروج بدون ذخیره
    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()