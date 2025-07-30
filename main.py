import pygame
import time
import json
import os
import sys
import random
import pygame
import json
import os

pygame.init()
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Login")

font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 18)
clock = pygame.time.Clock()

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = font.render(self.text, True, (0, 0, 0))

    def draw(self, screen):
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text

def auth_screen():
    username_box = InputBox(200, 100, 200, 40)
    password_box = InputBox(200, 160, 200, 40)
    password_hidden = ""

    current_user = None
    message = ""
    mode = "login"  # or "register"

    running = True
    while running:
        screen.fill((245, 245, 245))
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            username_box.handle_event(event)
            password_box.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if password_box.active:
                    if event.key == pygame.K_BACKSPACE:
                        password_hidden = password_hidden[:-1]
                    else:
                        password_hidden += event.unicode

                if event.key == pygame.K_TAB:
                    username_box.active = not username_box.active
                    password_box.active = not password_box.active

                if event.key == pygame.K_RETURN:
                    users = load_users()
                    username = username_box.get_text()
                    password = password_hidden

                    if mode == "login":
                        if username in users and users[username] == password:
                            current_user = username
                            running = False
                        else:
                            message = "Invalid credentials"
                    else:  # Register
                        if username in users:
                            message = "Username already exists"
                        else:
                            users[username] = password
                            save_users(users)
                            message = "Registration successful. Now login."
                            mode = "login"
                            password_hidden = ""
                            password_box.text = ""

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if 150 <= mx <= 280 and 220 <= my <= 260:
                    mode = "login"
                    message = ""
                elif 320 <= mx <= 450 and 220 <= my <= 260:
                    mode = "register"
                    message = ""

        username_box.draw(screen)
        password_box.draw(screen)

        # Labels
        screen.blit(font.render("Username:", True, (0, 0, 0)), (100, 105))
        screen.blit(font.render("Password:", True, (0, 0, 0)), (100, 165))
        screen.blit(small_font.render("Press Enter to continue", True, (100, 100, 100)), (200, 210))

        pygame.draw.rect(screen, (200, 200, 255), (150, 220, 130, 40))
        pygame.draw.rect(screen, (200, 255, 200), (320, 220, 130, 40))
        screen.blit(font.render("Login", True, (0, 0, 0)), (180, 230))
        screen.blit(font.render("Register", True, (0, 0, 0)), (340, 230))

        if message:
            screen.blit(small_font.render(message, True, (255, 0, 0)), (200, 280))

        pygame.display.flip()
        clock.tick(30)

    return current_user


# ------------ User Login and Registration ------------
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
            sys.exit()
        else:
            print("Invalid option.")

# ------------ Basic Sudoku Game Setup (Sample) ------------

pygame.init()
WIDTH, HEIGHT = 540, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")
font = pygame.font.SysFont("comicsans", 40)
small_font = pygame.font.SysFont("comicsans", 20)

# A sample easy Sudoku board
easy_board = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

def draw_board(board):
    screen.fill((255, 255, 255))

    gap = WIDTH // 9

    for i in range(10):
        thick = 4 if i % 3 == 0 else 1
        pygame.draw.line(screen, (0, 0, 0), (0, i * gap), (WIDTH, i * gap), thick)
        pygame.draw.line(screen, (0, 0, 0), (i * gap, 0), (i * gap, WIDTH), thick)

    for i in range(9):
        for j in range(9):
            if board[i][j] != 0:
                text = font.render(str(board[i][j]), True, (0, 0, 0))
                screen.blit(text, (j * gap + 20, i * gap + 10))

def game_loop():
    run = True
    selected = None
    board = [row[:] for row in easy_board]  # Copy of the board

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        draw_board(board)
        pygame.display.update()

    pygame.quit()

# ------------ Run the Full Program ------------

if __name__ == "__main__":
    current_user = auth_screen()
    print(f"\nHello, {current_user}! Let's play Sudoku.\nLaunching game...")
    time.sleep(1)
    game_loop()
