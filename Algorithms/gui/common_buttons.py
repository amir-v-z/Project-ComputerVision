import tkinter as tk

# Hover Effects
def on_enter(button, color):
    button["bg"] = color

def on_leave(button, color):
    button["bg"] = color

# Select Image Button
def create_open_button(parent, command):

    normal_color = "#27AE60"
    hover_color = "#2ECC71"

    open_btn = tk.Button(
        parent,
        text="📂 Select Image",
        font=("Segoe UI", 11, "bold"),
        bg=normal_color,
        fg="white",
        activebackground=hover_color,
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=15,
        pady=8,
        cursor="hand2",
        command=command
    )

    open_btn.pack(side="left", padx=10)

    open_btn.bind(
        "<Enter>",
        lambda e: on_enter(open_btn, hover_color)
    )

    open_btn.bind(
        "<Leave>",
        lambda e: on_leave(open_btn, normal_color)
    )

    return open_btn

# Save Image Button
def create_save_button(parent, command):

    normal_color = "#2980B9"
    hover_color = "#3498DB"

    save_btn = tk.Button(
        parent,
        text="💾 Save Image",
        font=("Segoe UI", 11, "bold"),
        bg=normal_color,
        fg="white",
        activebackground=hover_color,
        activeforeground="white",
        relief="flat",
        bd=0,
        padx=15,
        pady=8,
        cursor="hand2",
        command=command
    )

    save_btn.pack(side="left", padx=10)

    save_btn.bind(
        "<Enter>",
        lambda e: on_enter(save_btn, hover_color)
    )

    save_btn.bind(
        "<Leave>",
        lambda e: on_leave(save_btn, normal_color)
    )

    return save_btn