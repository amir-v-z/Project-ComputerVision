import tkinter as tk
from tkinter import messagebox
import time
import cv2

from filters.sharpen import (
    sharpen_light,
    sharpen_strong,
    sharpen_very_strong
)

from gui.common_buttons import create_open_button, create_save_button
from utils.image_io import open_image, save_image
from utils.display import show_image

class SharpenPage(tk.Frame):

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

        # ===== Sharpen Modes =====

        tk.Label(
            top_frame,
            text="Sharpen Type :",
            bg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=(10,5))

        self.sharpen_var = tk.StringVar(value="light")

        tk.Radiobutton(
            top_frame,
            text="Light (5)",
            variable=self.sharpen_var,
            value="light",
            bg="white"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            top_frame,
            text="Strong (9)",
            variable=self.sharpen_var,
            value="strong",
            bg="white"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            top_frame,
            text="Very Strong (13)",
            variable=self.sharpen_var,
            value="very_strong",
            bg="white"
        ).pack(side="left", padx=5)

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
        tk.Label(left_frame,text="Original Image", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.original_label = tk.Label(left_frame, bg="gray")
        self.original_label.pack()

        # Processed Image
        right_frame = tk.Frame(img_frame, bg="white")
        right_frame.pack(side="right", expand=True)
        tk.Label(right_frame, text="Sharpen Result", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.processed_label = tk.Label(right_frame, bg="gray")
        self.processed_label.pack()

    def process_image(self):

        image, path = open_image()

        if image is None:
            return

        self.original_image = image

        start = time.time()

        mode = self.sharpen_var.get()

        if mode == "light":
            result = sharpen_light(image)

        elif mode == "strong":
            result = sharpen_strong(image)

        elif mode == "very_strong":
            result = sharpen_very_strong(image)

        end = time.time()

        self.time_label.config(text=f"Execution Time : {end - start:.4f} sec")

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

        image_rgb = cv2.cvtColor(
            self.processed_image,
            cv2.COLOR_BGR2RGB
        )

        save_image(image_rgb)