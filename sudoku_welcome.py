# sudoku_welcome.py

import customtkinter as ctk

# Appearance settings
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# App setup
app = ctk.CTk()
app.geometry("400x300")
app.title("Welcome to Sudoku")

def go_to_auth():
    app.withdraw()  # Hide instead of destroy
    import sudoku_auth


frame = ctk.CTkFrame(master=app)
frame.pack(pady=50, padx=30, fill="both", expand=True)

label_title = ctk.CTkLabel(frame, text="Welcome to Sudoku!", font=("Arial", 24, "bold"))
label_title.pack(pady=30)

start_button = ctk.CTkButton(frame, text="Get Started", command=go_to_auth)
start_button.pack(pady=10)

app.mainloop()
