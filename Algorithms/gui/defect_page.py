import tkinter as tk
from tkinter import messagebox
import time

from filters.surface_defect import surface_defect_detection
from gui.common_buttons import create_open_button, create_save_button
from utils.image_io import open_image, save_image
from utils.display import show_image

class DefectPage(tk.Frame):

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

        # Element Size
        tk.Label(top_frame, text="Element Size :", bg="white", font=("Arial", 11)).pack(side="left", padx=2)
        self.size_entry = tk.Entry(top_frame, width=5, font=("Arial", 11))
        self.size_entry.insert(0, "5")
        self.size_entry.pack(side="left", padx=5)

        # Threshold
        tk.Label(top_frame, text="Threshold :", bg="white", font=("Arial", 11)).pack(side="left", padx=2)
        self.thresh_entry = tk.Entry(top_frame, width=5, font=("Arial", 11))
        self.thresh_entry.insert(0, "100")
        self.thresh_entry.pack(side="left", padx=5)

        # ===== Filter Modes =====

        self.mode_var = tk.StringVar(value="counting")
        
        tk.Radiobutton(
            top_frame, text="Counting", variable=self.mode_var, 
            value="counting", bg="white", font=("Arial", 10)
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            top_frame, text="Averaging", variable=self.mode_var, 
            value="averaging", bg="white", font=("Arial", 10)
        ).pack(side="left", padx=5)

        # Save Image Button
        create_save_button(top_frame, self.save_processed)

        # Processing time
        self.time_label = tk.Label(self, text="Execution Time :", bg="white", font=("Arial", 11))
        self.time_label.pack()

        # Lesion detection status
        self.status_label = tk.Label(
            self, text="Status: Waiting for Image", 
            bg="white", font=("Arial", 14, "bold"), fg="#34495E"
        )
        self.status_label.pack(pady=5)

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
        tk.Label(right, text="Defect Detection Result", bg="white", font=("Arial", 14, "bold")).pack(pady=10)
        self.processed_label = tk.Label(right, bg="gray")
        self.processed_label.pack()

    def process_image(self):

        img, _ = open_image()
        if img is None:
            return

        self.original_image = img

        try:
            size = int(self.size_entry.get())
            thresh = int(self.thresh_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Size and Threshold must be integers")
            return

        start = time.time()
        
        # Algorithm call
        result, found = surface_defect_detection(
            img, 
            size, 
            thresh, 
            self.mode_var.get()
        )
        
        end = time.time()

        self.processed_image = result

        self.time_label.config(text=f"Execution Time : {end - start:.4f} sec")

        # Status Update
        if found:
            self.status_label.config(text=f"⚠️ DEFECT DETECTED!", fg="#E74C3C")
        else:
            self.status_label.config(text=f"✅ SURFACE IS CLEAN", fg="#27AE60")

        show_image(self.original_label, img)
        show_image(self.processed_label, result)

    def save_processed(self):
        if self.processed_image is None:
            messagebox.showwarning("Warning", "No processed image to save")
            return

        save_image(self.processed_image)