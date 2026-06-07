import tkinter as tk
import webbrowser

class Sidebar(tk.Frame):

    def __init__(self, parent):
        super().__init__(parent, bg="#2C3E50", width=220)

        self.callback = None
        self.buttons = {}
        self.active_button = None

        self.pack_propagate(False)

        title = tk.Label(self, text="Algorithms", bg="#2C3E50", fg="white",  font=("Arial Rounded MT Bold", 18))

        title.pack(pady=20)

        # buttons
        self.create_button("Median", "median")
        self.create_button("Average", "average")
        self.create_button("Sharpening", "sharpen")
        self.create_button("Edge Detection", "edge")
        self.create_button("Defect Detection", "defect")

        # Exit button
        exit_btn = tk.Button(
            self,
            text="⛔ Exit",
            font=("consolas", 12),
            bg="#E74C3C",
            fg="white",
            relief="flat",
            padx=10,
            pady=8,
            cursor="hand2",
            command=self.exit_app
        )

        exit_btn.pack(side="bottom", fill="x", padx=15, pady=10)

        footer = tk.Label(
            self,
            text="Developed by amir_v_z",
            bg="#2C3E50",
            fg="#BDC3C7",
            font=("Arial", 10, "italic"),
            cursor="hand2"
        )

        footer.pack(side="bottom", pady=15)

        footer.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://github.com/amir-v-z")
        )

    def set_page_callback(self, callback):
        self.callback = callback

    def create_button(self, text, page_name):

        btn = tk.Button(
            self,
            text=text,
            font=("consolas", 13),
            bg="#34495E",
            fg="white",
            relief="flat",
            padx=10,
            pady=10,
            anchor="w",
            cursor="hand2",
            command=lambda: self.change_page(page_name)
        )

        btn.pack(fill="x", padx=15, pady=5)

        # hover effects
        btn.bind("<Enter>", lambda e: self.on_hover(btn))
        btn.bind("<Leave>", lambda e: self.on_leave(btn))

        self.buttons[page_name] = btn

    def on_hover(self, btn):
        if btn != self.active_button:
            btn.config(bg="#3E5C76")

    def on_leave(self, btn):
        if btn != self.active_button:
            btn.config(bg="#34495E")

    def change_page(self, page_name):

            if self.active_button:
                self.active_button.config(bg="#34495E")

            btn = self.buttons[page_name]
            btn.config(bg="#1ABC9C")

            self.active_button = btn

            if self.callback:
                self.callback(page_name)

    def exit_app(self):
        self.winfo_toplevel().destroy()