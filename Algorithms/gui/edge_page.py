import tkinter as tk
from tkinter import messagebox
import time

from filters.edge import (
    edge_detection_manual,
    edge_detection_opencv,
    sobel_edge_detection,
    log_edge_detection,
    canny_edge_detection,
    default_edge_kernel
)

from gui.common_buttons import create_open_button, create_save_button
from utils.image_io import open_image, save_image
from utils.display import show_image

class EdgePage(tk.Frame):

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

        # Threshold
        tk.Label(top_frame, text="Threshold :", bg="white", font=("Arial", 12)).pack(side="left")

        self.threshold_entry = tk.Entry(top_frame, width=5, font=("Arial", 12))
        self.threshold_entry.insert(0, "100")
        self.threshold_entry.pack(side="left", padx=10)

        # ===== Modes =====

        self.mode_var = tk.StringVar(value="manual")

        mode_frame = tk.Frame(top_frame, bg="white")
        mode_frame.pack(side="left", padx=20)

        # first row
        row1 = tk.Frame(mode_frame, bg="white")
        row1.pack()

        tk.Radiobutton(
            row1,
            text="Manual",
            variable=self.mode_var,
            value="manual",
            bg="white"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            row1,
            text="OpenCV",
            variable=self.mode_var,
            value="opencv",
            bg="white"
        ).pack(side="left", padx=5)

        # second row
        row2 = tk.Frame(mode_frame, bg="white")
        row2.pack()

        tk.Radiobutton(
            row2,
            text="Sobel",
            variable=self.mode_var,
            value="sobel",
            bg="white"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            row2,
            text="LoG",
            variable=self.mode_var,
            value="log",
            bg="white"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            row2,
            text="Canny",
            variable=self.mode_var,
            value="canny",
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
        left = tk.Frame(img_frame, bg="white")
        left.pack(side="left", expand=True)
        tk.Label(left, text="Original Image", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.original_label = tk.Label(left, bg="gray")
        self.original_label.pack()

        # Processed Image
        right = tk.Frame(img_frame, bg="white")
        right.pack(side="right", expand=True)
        tk.Label(right, text="Edge Detection Result", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.processed_label = tk.Label(right, bg="gray")
        self.processed_label.pack()

    def process_image(self):

        img, _ = open_image()
        if img is None:
            return

        self.original_image = img

        try:
            threshold = int(self.threshold_entry.get())
        except:
            messagebox.showerror("Error", "Threshold must be integer")
            return

        start = time.time()

        mode = self.mode_var.get()

        if mode == "manual":
            result = edge_detection_manual(
                img,
                default_edge_kernel,
                threshold
            )

        elif mode == "opencv":
            result = edge_detection_opencv(
                img,
                default_edge_kernel,
                threshold
            )

        elif mode == "sobel":
            result = sobel_edge_detection(img)

        elif mode == "log":
            result = log_edge_detection(img)

        elif mode == "canny":
            result = canny_edge_detection(img)

        end = time.time()

        self.processed_image = result

        self.time_label.config(text=f"Execution Time : {end - start:.4f} sec")

        show_image(self.original_label, img)
        show_image(self.processed_label, result)

    def save_processed(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image")
            return

        save_image(self.processed_image)