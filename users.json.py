import json
import os

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def register_user():
    users = load_users()
    username = input("Enter new username: ")
    if username in users:
        print("Username already exists.")
        return None
    password = input("Enter new password: ")
    users[username] = password
    save_users(users)
    print("Registration successful!")
    return username

def login_user():
    users = load_users()
    username = input("Username: ")
    password = input("Password: ")
    if username in users and users[username] == password:
        print("Login successful!")
        return username
    print("Invalid credentials.")
    return None

def auth_screen():
    while True:
        print("\n--- Welcome to Sudoku ---")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            user = login_user()
            if user:
                return user
        elif choice == "2":
            user = register_user()
            if user:
                return user
        elif choice == "3":
            exit()
        else:
            print("Invalid option.")
