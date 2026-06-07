import tkinter as tk
from tkinter import messagebox
import time
import cv2

from filters.average import average_filter
from gui.common_buttons import create_open_button, create_save_button
from utils.image_io import open_image, save_image
from utils.display import show_image

class AveragePage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="white")

        self.original_image = None
        self.processed_image = None

        self.build_ui()

    def build_ui(self):

        # ===== Top Controls =====

        top_frame = tk.Frame(self, bg="white")
        top_frame.pack(pady=20)

        # Select Image Button
        create_open_button(top_frame, self.process_image)

        # kernel entry
        tk.Label(top_frame, text="Kernel Size :", bg="white", font=("Arial", 12)).pack(side="left")

        self.kernel_entry = tk.Entry(top_frame, width=5, font=("Arial", 12))
        self.kernel_entry.insert(0, "3")
        self.kernel_entry.pack(side="left", padx=10)

        # Save Image Button
        create_save_button(top_frame, self.save_processed)

        # Processing time
        self.time_label = tk.Label(self, text="Execution Time :", bg="white", font=("Arial", 11))
        self.time_label.pack()

        # Image Display Area
        img_frame = tk.Frame(self, bg="white")
        img_frame.pack(expand=True, fill="both", pady=20)

        # Original Image
        left = tk.Frame(img_frame, bg="white")
        left.pack(side="left", expand=True)
        tk.Label(left, text="Original Image", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.original_label = tk.Label(left, bg="gray")
        self.original_label.pack()

        # Processed Image
        right = tk.Frame(img_frame, bg="white")
        right.pack(side="right", expand=True)
        tk.Label(right, text="Average Result", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.processed_label = tk.Label(right, bg="gray")
        self.processed_label.pack()

    def process_image(self):

        img, path = open_image()
        if img is None:
            return

        self.original_image = img

        # kernel size
        try:
            k = int(self.kernel_entry.get())
            if k <= 1:
                raise ValueError
        except:
            messagebox.showerror("Error", "Kernel size must be integer > 1")
            return

        start = time.time()
        result = average_filter(img, k)
        end = time.time()

        self.processed_image = result

        self.time_label.config(text=f"Execution Time : {end - start:.4f} sec")

        show_image(self.original_label, img)
        show_image(self.processed_label, result)

    def save_processed(self):

        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image")
            return

        rgb = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB)
        save_image(rgb)