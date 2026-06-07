from tkinter import filedialog
from PIL import Image
import cv2

def open_image():
    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp")
        ]
    )

    if not file_path:
        return None, None

    image = cv2.imread(file_path)

    return image, file_path

def save_image(image_rgb):

    image = Image.fromarray(image_rgb)

    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("JPEG", "*.jpg")
        ]
    )

    if file_path:
        image.save(file_path)