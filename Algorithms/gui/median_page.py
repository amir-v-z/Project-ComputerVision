import tkinter as tk
from tkinter import messagebox
import time
import cv2

from filters.median import (
    median_filter_manual,
    median_filter_opencv
)

from gui.common_buttons import create_open_button, create_save_button
from utils.image_io import open_image, save_image
from utils.display import show_image

class MedianPage(tk.Frame):

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

        # Kernel Size
        kernel_label = tk.Label(top_frame, text="Kernel Size :", bg="white", font=("Arial", 12))

        kernel_label.pack(side="left")

        self.kernel_entry = tk.Entry(top_frame, width=5, font=("Arial", 12))

        self.kernel_entry.insert(0, "3")
        self.kernel_entry.pack(side="left", padx=10)

        # ===== Filter Modes =====

        self.mode_var = tk.StringVar(value="manual")

        manual_radio = tk.Radiobutton(
            top_frame,
            text="Manual",
            variable=self.mode_var,
            value="manual",
            bg="white"
        )

        manual_radio.pack(side="left", padx=10)

        opencv_radio = tk.Radiobutton(
            top_frame,
            text="OpenCV",
            variable=self.mode_var,
            value="opencv",
            bg="white"
        )

        opencv_radio.pack(side="left", padx=10)

        # Save Image Button
        create_save_button(top_frame, self.save_processed)

        # Processing time
        self.time_label = tk.Label(self, text="Execution Time :", bg="white", font=("Arial", 11))
        self.time_label.pack()

        # Image Display Area
        img_frame = tk.Frame(self, bg="white")
        img_frame.pack(expand=True, fill="both", pady=20)

        # Original Image
        left_frame = tk.Frame(img_frame, bg="white")
        left_frame.pack(side="left", expand=True)
        tk.Label(left_frame, text="Original Image", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.original_label = tk.Label(left_frame, bg="gray")
        self.original_label.pack()

        # Processed Image
        right_frame = tk.Frame(img_frame, bg="white")
        right_frame.pack(side="right", expand=True)
        tk.Label(right_frame, text="Median Result", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.processed_label = tk.Label(right_frame, bg="gray")
        self.processed_label.pack()

    def process_image(self):

        image, path = open_image()

        if image is None:
            return

        self.original_image = image

        try:
            kernel_size = int(self.kernel_entry.get())

            if kernel_size % 2 == 0 or kernel_size <= 0:
                raise ValueError

        except:
            messagebox.showerror(
                "Error",
                "Kernel size must be positive odd number"
            )
            return

        start = time.time()

        mode = self.mode_var.get()

        if mode == "manual":
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = median_filter_manual(rgb_image, kernel_size)

        elif mode == "opencv":
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = median_filter_opencv(rgb_image, kernel_size)

        end = time.time()

        self.time_label.config(
            text=f"Execution Time : {end - start:.4f} sec"
        )

        self.processed_image = result

        show_image(self.original_label, image)
        show_image(self.processed_label, result)

    def save_processed(self):

        if self.processed_image is None:
            messagebox.showwarning(
                "Warning",
                "No processed image"
            )
            return

        if len(self.processed_image.shape) == 3:

            image_rgb = cv2.cvtColor(
                self.processed_image,
                cv2.COLOR_BGR2RGB
            )

        else:
            image_rgb = self.processed_image

        save_image(image_rgb)