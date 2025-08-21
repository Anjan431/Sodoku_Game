import customtkinter as ctk
import tkinter.messagebox as mb
import json
import os

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def register_user():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    confirm = entry_confirm.get().strip()

    if not username or not password or not confirm:
        mb.showerror("Error", "All fields are required.")
        return

    if password != confirm:
        mb.showerror("Error", "Passwords do not match.")
        return

    users = load_users()
    if username in users:
        mb.showerror("Error", "Username already exists.")
        return

    users[username] = password
    save_users(users)
    mb.showinfo("Success", "Registration successful!")

def go_back():
    root.destroy()
    # Replace this with actual call to login screen if needed

# ---------------- UI Setup ----------------
root = ctk.CTk()
root.geometry("400x400")
root.title("Sudoku Registration")
root.configure(fg_color="#2a379c")  # blue background like your screenshot

title = ctk.CTkLabel(root, text="Register for Sodoku", font=("Helvetica", 20, "bold"), text_color="gold")
title.pack(pady=30)

entry_username = ctk.CTkEntry(root, placeholder_text="Username", width=250)
entry_username.pack(pady=10)

entry_password = ctk.CTkEntry(root, placeholder_text="Enter password", show="*", width=250)
entry_password.pack(pady=10)

entry_confirm = ctk.CTkEntry(root, placeholder_text="Re-enter password", show="*", width=250)
entry_confirm.pack(pady=10)

frame_buttons = ctk.CTkFrame(root, fg_color="transparent")
frame_buttons.pack(pady=20)

btn_back = ctk.CTkButton(frame_buttons, text="← Back", command=go_back, width=100)
btn_back.grid(row=0, column=0, padx=10)

btn_register = ctk.CTkButton(frame_buttons, text="🗝 Register", command=register_user, width=100)
btn_register.grid(row=0, column=1, padx=10)

root.mainloop()
