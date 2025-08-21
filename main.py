import pygame
import sys
import random
import time
import copy
import json

# ---------------- Initialization ---------------- #
pygame.init()

WIDTH, HEIGHT = 540, 600
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
FONT = pygame.font.SysFont("comicsansms", 40, bold=True)
SMALL_FONT = pygame.font.SysFont("comicsansms", 28)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 180, 100)
RED = (230, 80, 80)
YELLOW = (255, 215, 0)
LIGHT_BLUE = (100, 180, 250)
LIGHT_GREEN = (100, 220, 120)
LIGHT_RED = (240, 120, 120)
BG_TOP = (70, 130, 250)
BG_BOTTOM = (200, 180, 250)
HOVER_TINT = (40, 40, 40)

# ---------------- Game State ---------------- #
current_screen = "login"
selected_cell = (-1, -1)
grid = [[0] * 9 for _ in range(9)]
original_grid = None
start_time = None
selected_difficulty = None

# Login System
users = {}
current_user = None
active_input = "username"
input_text = {"username": "", "password": ""}
login_message = ""

# ---------------- Persistent Storage ---------------- #
def load_users():
    global users
    try:
        with open("users.json", "r") as f:
            content = f.read().strip()
            if content:
                users = json.loads(content)
            else:
                users = {}
    except FileNotFoundError:
        users = {}

    for user, data in users.items():
        if "stats" not in data:
            data["stats"] = {
                "Easy": {"played": 0, "won": 0, "lost": 0, "best_time": None},
                "Medium": {"played": 0, "won": 0, "lost": 0, "best_time": None},
                "Hard": {"played": 0, "won": 0, "lost": 0, "best_time": None},
            }
        else:
            for level in ["Easy", "Medium", "Hard"]:
                if level not in data["stats"]:
                    data["stats"][level] = {
                        "played": 0,
                        "won": 0,
                        "lost": 0,
                        "best_time": None,
                    }

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

load_users()
save_users()

# ---------------- Helper Functions ---------------- #
def draw_text_centered(surface, text, y, font, color=BLACK):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (WIDTH // 2 - rendered.get_width() // 2, y))

def draw_grid():
    for i in range(GRID_SIZE + 1):
        lw = 3 if i % 3 == 0 else 1
        pygame.draw.line(WIN, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), lw)
        pygame.draw.line(WIN, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), lw)

def draw_numbers():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            num = grid[i][j]
            if num != 0:
                color = BLACK if original_grid[i][j] != 0 else BLUE
                text = FONT.render(str(num), True, color)
                WIN.blit(text, (j * CELL_SIZE + 20, i * CELL_SIZE + 10))

def draw_selected_cell():
    if selected_cell != (-1, -1):
        row, col = selected_cell
        pygame.draw.rect(
            WIN, BLUE, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3
        )

def get_elapsed_time():
    if start_time is None:
        return "00:00"
    elapsed = int(time.time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    return f"{minutes:02}:{seconds:02}"

def update_stats(user, level, won, elapsed_time=0):
    stats = users[user]["stats"][level]
    stats["played"] += 1
    if won:
        stats["won"] += 1
        if stats.get("best_time") is None or elapsed_time < stats["best_time"]:
            stats["best_time"] = elapsed_time
    else:
        stats["lost"] += 1
    save_users()

def draw_vertical_gradient():
    for y in range(HEIGHT):
        color = (
            BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * y // HEIGHT,
            BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * y // HEIGHT,
            BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * y // HEIGHT,
        )
        pygame.draw.line(WIN, color, (0, y), (WIDTH, y))

def draw_button(rect, color, text, hover=False):
    base_color = tuple(min(255, c + (HOVER_TINT[i] if hover else 0)) for i, c in enumerate(color))
    pygame.draw.rect(WIN, base_color, rect, border_radius=14)
    label = SMALL_FONT.render(text, True, BLACK if color != RED else WHITE)
    WIN.blit(label, (rect.x + (rect.width - label.get_width()) // 2, rect.y + (rect.height - label.get_height()) // 2))

# ---------------- Sudoku Logic ---------------- #
# Keep sudoku generation and validation logic same as before (omitted here for brevity)

# ---------------- Screens ---------------- #
def draw_login_screen(mouse_pos):
    draw_vertical_gradient()
    draw_text_centered(WIN, "🔑 Sudoku Login / Register", 50, FONT, YELLOW)

    username_box = pygame.Rect(WIDTH // 2 - 140, 140, 280, 50)
    password_box = pygame.Rect(WIDTH // 2 - 140, 220, 280, 50)

    login_btn = pygame.Rect(WIDTH // 2 - 130, 320, 120, 50)
    reg_btn = pygame.Rect(WIDTH // 2 + 10, 320, 120, 50)

    pygame.draw.rect(WIN, WHITE, username_box, border_radius=12)
    pygame.draw.rect(WIN, WHITE, password_box, border_radius=12)

    WIN.blit(SMALL_FONT.render("Username", True, BLACK), (username_box.x, username_box.y - 28))
    WIN.blit(SMALL_FONT.render("Password", True, BLACK), (password_box.x, password_box.y - 28))

    WIN.blit(SMALL_FONT.render(input_text["username"], True, BLACK), (username_box.x + 10, username_box.y + 10))
    pwd_display = "*" * len(input_text["password"])
    WIN.blit(SMALL_FONT.render(pwd_display, True, BLACK), (password_box.x + 10, password_box.y + 10))

    draw_button(login_btn, GREEN, "Login", login_btn.collidepoint(mouse_pos))
    draw_button(reg_btn, RED, "Register", reg_btn.collidepoint(mouse_pos))

    if login_message:
        draw_text_centered(WIN, login_message, 400, SMALL_FONT, WHITE)

    pygame.display.update()
    return username_box, password_box, login_btn, reg_btn

def draw_menu(mouse_pos):
    draw_vertical_gradient()
    draw_text_centered(WIN, "🎮 Select Difficulty", 50, FONT, YELLOW)

    buttons = {}
    colors = {"Easy": LIGHT_GREEN, "Medium": LIGHT_BLUE, "Hard": LIGHT_RED}
    for idx, level in enumerate(["Easy", "Medium", "Hard"]):
        btn = pygame.Rect(WIDTH // 2 - 90, 150 + idx * 100, 180, 60)
        draw_button(btn, colors[level], level, btn.collidepoint(mouse_pos))
        buttons[level] = btn

    history_btn = pygame.Rect(WIDTH // 2 - 90, 500, 180, 50)
    draw_button(history_btn, YELLOW, "📜 History", history_btn.collidepoint(mouse_pos))
    buttons["History"] = history_btn

    pygame.display.update()
    return buttons

def draw_history_screen(username):
    draw_vertical_gradient()
    draw_text_centered(WIN, f"{username}'s History", 50, FONT, YELLOW)

    levels = [("Easy", LIGHT_GREEN), ("Medium", LIGHT_BLUE), ("Hard", LIGHT_RED)]
    y_start = 130
    for level, color in levels:
        stats = users[username]["stats"].get(level, {"played": 0, "won": 0, "lost": 0, "best_time": None})
        draw_text_centered(WIN, f"{level}:", y_start, SMALL_FONT, color)
        draw_text_centered(WIN, f"Played: {stats['played']}   ✅ Won: {stats['won']}   ❌ Lost: {stats['lost']}", y_start + 30, SMALL_FONT, WHITE)
        best_time = stats.get("best_time")
        if best_time:
            minutes = best_time // 60
            seconds = best_time % 60
            draw_text_centered(WIN, f"🎯 Best Time: {minutes:02}:{seconds:02}", y_start + 60, SMALL_FONT, YELLOW)
        y_start += 120

    draw_text_centered(WIN, "Press ESC to return", HEIGHT - 70, SMALL_FONT, WHITE)
    pygame.display.update()

def draw_game():
    WIN.fill(WHITE)
    draw_grid()
    draw_numbers()
    draw_selected_cell()
    timer_text = SMALL_FONT.render("⏱ Time: " + get_elapsed_time(), True, BLACK)
    WIN.blit(timer_text, (20, HEIGHT - 40))
    pygame.display.update()

def draw_win_screen(mouse_pos):
    draw_vertical_gradient()
    draw_text_centered(WIN, "🎉 Congratulations! 🎉", 80, FONT, YELLOW)
    draw_text_centered(WIN, f"Your Time: {get_elapsed_time()}", 150, SMALL_FONT, WHITE)

    play_again_btn = pygame.Rect(WIDTH // 2 - 110, 250, 220, 60)
    menu_btn = pygame.Rect(WIDTH // 2 - 110, 350, 220, 60)

    draw_button(play_again_btn, LIGHT_BLUE, "▶ Play Again", play_again_btn.collidepoint(mouse_pos))
    draw_button(menu_btn, LIGHT_GREEN, "🏠 Main Menu", menu_btn.collidepoint(mouse_pos))

    pygame.display.update()
    return play_again_btn, menu_btn

# ---------------- Main Loop ---------------- #
def main():
    global current_screen, selected_cell, active_input, input_text, login_message, selected_difficulty, current_user, start_time
    clock = pygame.time.Clock()
    history_screen_open = False
    play_again_btn = None
    menu_btn = None

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        if current_screen == "login":
            username_box, password_box, login_btn, reg_btn = draw_login_screen(mouse_pos)
        elif current_screen == "home":
            buttons = draw_menu(mouse_pos)
        elif current_screen == "history" and history_screen_open:
            draw_history_screen(current_user)
        elif current_screen == "game":
            draw_game()
            # check win condition here (unchanged)
        elif current_screen == "win":
            play_again_btn, menu_btn = draw_win_screen(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_users()
                pygame.quit()
                sys.exit()
            # ... (handle input same as before) ...

if __name__ == "__main__":
    main()
