import tkinter as tk
from gui.sidebar import Sidebar
from gui.default_page import DefaultPage
from gui.median_page import MedianPage
from gui.average_page import AveragePage
from gui.sharpen_page import SharpenPage
from gui.edge_page import EdgePage
from gui.defect_page import DefectPage

root = tk.Tk()
root.title("Image Processing Tool")
root.geometry("1200x700")

# ===== Sidebar =====
sidebar = Sidebar(root)
sidebar.pack(side="left", fill="y")

# ===== Main Area =====
main_area = tk.Frame(root, bg="white")
main_area.pack(side="right", expand=True, fill="both")

current_page = None

def show_page(page_name):
    global current_page

    if current_page is not None:
        current_page.destroy()

    if page_name == "default":
        current_page = DefaultPage(main_area)
    elif page_name == "median":
        current_page = MedianPage(main_area)
    elif page_name == "average":
        current_page = AveragePage(main_area)
    elif page_name == "sharpen":
        current_page = SharpenPage(main_area)
    elif page_name == "edge":
        current_page = EdgePage(main_area)
    elif page_name == "defect":
        current_page = DefectPage(main_area)

    current_page.pack(expand=True, fill="both")

# Connecting sidebar buttons
sidebar.set_page_callback(show_page)

# Default page
show_page("default")

root.mainloop()