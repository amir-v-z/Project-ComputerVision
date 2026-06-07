import tkinter as tk

class DefaultPage(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="white")

        self.build_ui()

    def build_ui(self):

        container = tk.Frame(self, bg="white")
        container.pack(expand=True)

        title = tk.Label(
            container,
            text="Image Processing App",
            font=("Arial Rounded MT Bold", 26),
            bg="white",
            fg="#2C3E50"
        )
        title.pack(pady=20)

        message = tk.Label(
            container,
            text="Hi, Select an algorithm from the left panel.",
            font=("comic sans MS", 20),
            bg="white",
            fg="#555"
        )
        message.pack(pady=10)