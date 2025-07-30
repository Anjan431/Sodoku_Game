# sudoku_auth.py
import customtkinter as ctk
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("400x400")
app.title("Sudoku Login/Register")

def open_game():
    app.destroy()
    import sudoku_game
    sudoku_game.run_game()

frame = ctk.CTkFrame(master=app)
frame.pack(pady=40, padx=20, fill="both", expand=True)

ctk.CTkLabel(frame, text="Welcome to Sudoku", font=("Arial", 24, "italic")).pack(pady=20)
ctk.CTkButton(frame, text="Login", command=open_game).pack(pady=10)
ctk.CTkButton(frame, text="Register", command=open_game).pack(pady=10)

app.mainloop()
