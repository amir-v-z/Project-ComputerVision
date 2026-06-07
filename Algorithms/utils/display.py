from PIL import Image, ImageTk
import cv2

def show_image(label, image_array):

    if len(image_array.shape) == 3:
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)

    image = Image.fromarray(image_array)

    image.thumbnail((400, 400))

    photo = ImageTk.PhotoImage(image)

    label.config(image=photo)
    label.image = photo