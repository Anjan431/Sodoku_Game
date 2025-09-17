import numpy as np
import pygame
import sys
import random
import time
import copy
import json
import os

# ---------------- Initialization ---------------- #
pygame.init()
try:
    pygame.mixer.init()
except Exception:
    pass  # audio optional

WIDTH, HEIGHT = 540, 600
GRID_SIZE = 9

# Board geometry (single source of truth)
BOARD_MARGIN = 20  # margin from window edge
BOARD_SIZE = WIDTH - 2 * BOARD_MARGIN
CELL_SIZE = BOARD_SIZE // GRID_SIZE
BOARD_X, BOARD_Y = BOARD_MARGIN, BOARD_MARGIN

FONT = pygame.font.SysFont("comicsans", 40)
SMALL_FONT = pygame.font.SysFont("comicsans", 28)
TINY_FONT = pygame.font.SysFont("comicsans", 22)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 150, 0)
RED = (255, 0, 0)


current_screen = "login"
selected_cell = (-1, -1)
grid = [[0]*9 for _ in range(9)]
original_grid = None
start_time = None
selected_difficulty = None


users = {}  # Loaded from JSON
current_user = None
active_input = "username"
input_text = {"username": "", "password": ""}
login_message = ""


pulse_value = 0
pulse_direction = 1
button_hover_alpha = {}  # key -> 0..255
button_pressed_alpha = {}  # transient press effect


def create_tone(frequency=440, duration_ms=300, volume=0.5):

    sample_rate = 44100
    n_samples = int(sample_rate * (duration_ms / 1000.0))
    t = np.linspace(0, duration_ms / 1000.0, n_samples, False)
    wave = np.sin(frequency * 2 * np.pi * t) * volume
    audio = np.int16(wave * 32767)
    stereo = np.column_stack((audio, audio))
    return pygame.sndarray.make_sound(stereo)

WIN_SOUND = None
LOSE_SOUND = None
if pygame.mixer.get_init():
    try:
        WIN_SOUND = create_tone(880, 300, 0.5)   # Cheerful high tone
        LOSE_SOUND = create_tone(220, 600, 0.5)  # Low buzz
    except Exception:
        WIN_SOUND = None
        LOSE_SOUND = None

def play_win():
    if WIN_SOUND:
        try:
            WIN_SOUND.play()
        except Exception:
            pass

def play_lose():
    if LOSE_SOUND:
        try:
            LOSE_SOUND.play()
        except Exception:
            pass


CLICK_SOUND = None
def safe_load_sound(path):
    if not pygame.mixer.get_init():
        return None
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            return None
    return None

def try_start_bgm(path, volume=0.25):
    if not pygame.mixer.get_init():
        return
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
        except Exception:
            pass


CLICK_SOUND = safe_load_sound("click.wav")
try_start_bgm("bgm.mp3", volume=0.18)

def play_click():
    if CLICK_SOUND:
        try:
            CLICK_SOUND.play()
        except Exception:
            pass


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
                "Hard": {"played": 0, "won": 0, "lost": 0, "best_time": None}
            }
        else:
            for level in ["Easy", "Medium", "Hard"]:
                if level not in data["stats"]:
                    data["stats"][level] = {"played": 0, "won": 0, "lost": 0, "best_time": None}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

load_users()
save_users()


def draw_text_centered(surface, text, y, font, color=BLACK):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (WIDTH//2 - rendered.get_width()//2, y))

def draw_vertical_gradient(surface, top_rgb, bottom_rgb):
    r1, g1, b1 = top_rgb
    r2, g2, b2 = bottom_rgb
    for i in range(HEIGHT):
        t = i / max(1, HEIGHT-1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        pygame.draw.line(surface, (r, g, b), (0, i), (WIDTH, i))

def update_pulse(speed=2, max_amp=40):
    global pulse_value, pulse_direction
    pulse_value += pulse_direction * speed
    if pulse_value > max_amp or pulse_value < 0:
        pulse_direction *= -1
    return pulse_value

def draw_chip(text, pos, bg=(30, 30, 50), fg=(230, 230, 255)):
    pad_x, pad_y = 10, 6
    surf = TINY_FONT.render(text, True, fg)
    rect = surf.get_rect()
    rect.topleft = (pos[0] + pad_x, pos[1] + pad_y)
    box = pygame.Rect(pos[0], pos[1], rect.width + pad_x*2, rect.height + pad_y*2)
    pygame.draw.rect(WIN, bg, box, border_radius=12)
    pygame.draw.rect(WIN, (255, 255, 255), box, 1, border_radius=12)
    WIN.blit(surf, rect.topleft)

def draw_button(surface, rect, text, key, base_color=(60, 120, 200), hover_color=(110, 180, 255), text_color=(255, 255, 255)):
    # Hover alpha
    if key not in button_hover_alpha:
        button_hover_alpha[key] = 0
    if key not in button_pressed_alpha:
        button_pressed_alpha[key] = 0

    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        button_hover_alpha[key] = min(255, button_hover_alpha[key] + 18)
    else:
        button_hover_alpha[key] = max(0, button_hover_alpha[key] - 18)


    ha = button_hover_alpha[key]
    r = base_color[0] + (hover_color[0] - base_color[0]) * ha // 255
    g = base_color[1] + (hover_color[1] - base_color[1]) * ha // 255
    b = base_color[2] + (hover_color[2] - base_color[2]) * ha // 255
    color = (r, g, b)


    if button_pressed_alpha[key] > 0:
        button_pressed_alpha[key] = max(0, button_pressed_alpha[key] - 25)

    pygame.draw.rect(surface, color, rect, border_radius=14)
    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=14)


    if button_pressed_alpha[key] > 0:
        alpha = button_pressed_alpha[key]
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, alpha // 2))
        surface.blit(overlay, rect.topleft)

    txt = SMALL_FONT.render(text, True, text_color)
    surface.blit(txt, (rect.x + (rect.width - txt.get_width()) // 2,
                       rect.y + (rect.height - txt.get_height()) // 2))

def press_button(key):

    button_pressed_alpha[key] = 200
    play_click()

def get_elapsed_time():
    if start_time is None:
        return "00:00"
    elapsed = int(time.time()-start_time)
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


def is_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3*(row//3), 3*(col//3)
    for i in range(start_row,start_row+3):
        for j in range(start_col,start_col+3):
            if board[i][j]==num:
                return False
    return True

def solve_board(board):
    for i in range(9):
        for j in range(9):
            if board[i][j]==0:
                nums = list(range(1,10))
                random.shuffle(nums)
                for num in nums:
                    if is_valid(board,i,j,num):
                        board[i][j]=num
                        if solve_board(board):
                            return True
                        board[i][j]=0
                return False
    return True

def fill_diagonal_boxes(board):
    for i in range(0,9,3):
        fill_box(board,i,i)

def fill_box(board,row_start,col_start):
    nums = list(range(1,10))
    random.shuffle(nums)
    idx=0
    for i in range(3):
        for j in range(3):
            board[row_start+i][col_start+j]=nums[idx]
            idx+=1

def remove_cells(board,difficulty):
    levels = {"Easy":35,"Medium":45,"Hard":55}
    cells_to_remove = levels[difficulty]
    puzzle = copy.deepcopy(board)
    count=0
    while count<cells_to_remove:
        i=random.randint(0,8)
        j=random.randint(0,8)
        if puzzle[i][j]!=0:
            puzzle[i][j]=0
            count+=1
    return puzzle

def generate_full_board():
    board = [[0]*9 for _ in range(9)]
    fill_diagonal_boxes(board)
    solve_board(board)
    return board

def load_puzzle(difficulty):
    global grid, original_grid, start_time
    full_board = generate_full_board()
    grid = remove_cells(full_board,difficulty)
    original_grid = copy.deepcopy(grid)
    start_time = time.time()

def is_board_complete_and_valid(board):
    for row in board:
        if 0 in row:
            return False
    for i in range(9):
        if len(set(board[i]))!=9 or len(set([board[j][i] for j in range(9)]))!=9:
            return False
    for br in range(3):
        for bc in range(3):
            nums=[]
            for i in range(br*3,br*3+3):
                for j in range(bc*3,bc*3+3):
                    nums.append(board[i][j])
            if len(set(nums))!=9:
                return False
    return True

def conflicts_at(board, r, c, val):

    if val == 0:
        return []
    bad = []

    for j in range(9):
        if j != c and board[r][j] == val:
            bad.append((r, j))

    for i in range(9):
        if i != r and board[i][c] == val:
            bad.append((i, c))

    sr, sc = 3*(r//3), 3*(c//3)
    for i in range(sr, sr+3):
        for j in range(sc, sc+3):
            if (i, j) != (r, c) and board[i][j] == val:
                bad.append((i, j))

    if bad:
        bad.append((r, c))
    return bad

def flash_completed_board():
    for _ in range(3):
        draw_vertical_gradient(WIN, (20, 60, 90), (10, 20, 40))
        draw_grid_modern()
        draw_numbers_modern()
        pygame.display.update()
        pygame.time.delay(220)
        draw_vertical_gradient(WIN, (10, 20, 40), (20, 60, 90))
        draw_grid_modern()
        pygame.display.update()
        pygame.time.delay(220)


def move_to_next_editable_cell(row, col):
    total = GRID_SIZE * GRID_SIZE
    start_idx = row * GRID_SIZE + col
    for step in range(1, total + 1):
        idx = (start_idx + step) % total
        nr = idx // GRID_SIZE
        nc = idx % GRID_SIZE
        if original_grid[nr][nc] == 0:
            return (nr, nc)
    return (row, col)

def draw_grid_modern():

    panel = pygame.Rect(BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)
    pygame.draw.rect(WIN, (24, 28, 48), panel, border_radius=18)
    pygame.draw.rect(WIN, (255, 255, 255), panel, 2, border_radius=18)


    if selected_cell != (-1, -1):
        sr, sc = selected_cell
        # row & col soft highlight
        row_rect = pygame.Rect(BOARD_X, BOARD_Y + sr*CELL_SIZE, BOARD_SIZE, CELL_SIZE)
        col_rect = pygame.Rect(BOARD_X + sc*CELL_SIZE, BOARD_Y, CELL_SIZE, BOARD_SIZE)
        row_overlay = pygame.Surface((row_rect.width, row_rect.height), pygame.SRCALPHA)
        col_overlay = pygame.Surface((col_rect.width, col_rect.height), pygame.SRCALPHA)
        row_overlay.fill((80, 120, 180, 35))
        col_overlay.fill((80, 120, 180, 35))
        WIN.blit(row_overlay, row_rect.topleft)
        WIN.blit(col_overlay, col_rect.topleft)


    for i in range(GRID_SIZE+1):
        lw = 3 if i%3 == 0 else 1
        color = (170, 180, 210) if i%3 == 0 else (90, 100, 130)
        # horizontal
        y = BOARD_Y + i*CELL_SIZE
        pygame.draw.line(WIN, color, (BOARD_X, y), (BOARD_X + BOARD_SIZE, y), lw)
        # vertical
        x = BOARD_X + i*CELL_SIZE
        pygame.draw.line(WIN, color, (x, BOARD_Y), (x, BOARD_Y + BOARD_SIZE), lw)


    if selected_cell != (-1, -1):
        sr, sc = selected_cell
        p = update_pulse(speed=3, max_amp=30)
        glow = 120 + p  # 120..150
        rect = pygame.Rect(BOARD_X + sc*CELL_SIZE, BOARD_Y + sr*CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(WIN, (60, glow, 220), rect, 3, border_radius=8)

def draw_numbers_modern():
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            num = grid[r][c]
            if num != 0:
                base_color = (230, 235, 255) if original_grid[r][c] != 0 else (120, 190, 255)
                text = FONT.render(str(num), True, base_color)
                text_rect = text.get_rect(center=(BOARD_X + c * CELL_SIZE + CELL_SIZE // 2,
                                                  BOARD_Y + r * CELL_SIZE + CELL_SIZE // 2))
                WIN.blit(text, text_rect)


    if selected_cell != (-1, -1):
        r, c = selected_cell
        val = grid[r][c]
        confs = conflicts_at(grid, r, c, val)
        if confs:
            for (rr, cc) in confs:
                rect = pygame.Rect(BOARD_X + cc * CELL_SIZE, BOARD_Y + rr * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                overlay = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(overlay, (255, 70, 70, 80), overlay.get_rect(), border_radius=8)
                WIN.blit(overlay, rect.topleft)



def draw_login_screen():
    # Background gradient
    draw_vertical_gradient(WIN, (30, 30, 60), (12, 12, 30))
    update_pulse(2, 40)
    title_color = (255, 215 - pulse_value // 2, 0)
    draw_text_centered(WIN, "Sudoku Login / Register", 44, FONT, title_color)

    username_box = pygame.Rect(WIDTH//2-140, 130, 280, 54)
    password_box = pygame.Rect(WIDTH//2-140, 210, 280, 54)
    login_btn = pygame.Rect(WIDTH//2-150, 310, 130, 54)
    reg_btn = pygame.Rect(WIDTH//2+20, 310, 130, 54)


    for box, keyname in [(username_box, "username"), (password_box, "password")]:
        active = (active_input == keyname)
        pygame.draw.rect(WIN, (50, 50, 90), box, border_radius=12)
        border_col = (100 + (pulse_value*3) % 155, 200, 255) if active else (200, 200, 200)
        pygame.draw.rect(WIN, border_col, box, 3, border_radius=12)

        value = input_text[keyname] if keyname == "username" else "*"*len(input_text["password"])
        txt_surface = SMALL_FONT.render(value, True, (255, 255, 255))
        WIN.blit(txt_surface, (box.x + 10, box.y + 12))

    draw_text_centered(WIN, "Username", 100, SMALL_FONT, (180, 200, 255))
    draw_text_centered(WIN, "Password", 180, SMALL_FONT, (180, 200, 255))


    draw_button(WIN, login_btn, "Login", "login_btn", base_color=(50,150,100), hover_color=(70,220,140))
    draw_button(WIN, reg_btn, "Register", "reg_btn", base_color=(90,110,200), hover_color=(130,170,255))


    if login_message:
        draw_text_centered(WIN, login_message, 390, SMALL_FONT, RED)


    draw_text_centered(WIN, "TAB to switch fields • ENTER to submit", 560, TINY_FONT, (200, 200, 220))

    pygame.display.update()
    return username_box, password_box, login_btn, reg_btn

def draw_menu():
    draw_vertical_gradient(WIN, (25, 25, 55), (10, 10, 26))
    update_pulse(2, 40)
    title_color = (200, 200 - pulse_value // 2, 255)
    draw_text_centered(WIN, "Select Difficulty", 48, FONT, title_color)

    buttons={}
    levels = ["Easy", "Medium", "Hard"]
    for idx, level in enumerate(levels):
        btn = pygame.Rect(WIDTH//2-90, 140+idx*90, 180, 58)
        base = (70, 160, 110) if level == "Easy" else (160, 120, 80) if level == "Medium" else (150, 80, 100)
        hover = (110, 220, 160) if level == "Easy" else (210, 160, 110) if level == "Medium" else (220, 120, 150)
        draw_button(WIN, btn, level, f"menu_{level}", base_color=base, hover_color=hover)
        buttons[level]=btn

    history_btn = pygame.Rect(WIDTH//2-90, 430, 180, 50)
    draw_button(WIN, history_btn, "History", "menu_history", base_color=(80, 100, 180), hover_color=(130, 160, 240))
    buttons["History"]=history_btn


    if current_user:
        draw_chip(f"User: {current_user}", (12, 560), bg=(36,36,60))

    pygame.display.update()
    return buttons

def draw_history_screen(username):
    draw_vertical_gradient(WIN, (20, 20, 44), (8, 8, 20))
    draw_text_centered(WIN, f"{username}'s History", 40, FONT, (220, 220, 255))
    y_start = 120
    for level in ["Easy", "Medium", "Hard"]:
        stats = users[username]["stats"].get(level, {"played":0,"won":0,"lost":0,"best_time":None})
        draw_text_centered(WIN, f"{level}", y_start, SMALL_FONT, (200, 210, 255))
        draw_text_centered(WIN, f"Played: {stats['played']}  •  Won: {stats['won']}  •  Lost: {stats['lost']}", y_start+26, TINY_FONT, (230,230,240))
        best_time = stats.get("best_time")
        if best_time is not None:
            minutes = best_time // 60
            seconds = best_time % 60
            draw_text_centered(WIN, f"Best Time: {minutes:02}:{seconds:02}", y_start+48, TINY_FONT, (180,200,255))
        y_start += 110
    draw_text_centered(WIN, "Press ESC to return", 550, TINY_FONT, (210, 210, 230))
    pygame.display.update()

def draw_game():
    # BG
    draw_vertical_gradient(WIN, (14, 20, 36), (6, 10, 18))
    # Board
    draw_grid_modern()
    draw_numbers_modern()

    # HUD: timer + difficulty
    draw_chip("Time: " + get_elapsed_time(), (WIDTH-160, 560), bg=(30,30,50))
    if selected_difficulty:
        draw_chip(f"Difficulty: {selected_difficulty}", (12, 560), bg=(30,30,50))

    pygame.display.update()

def draw_win_screen():
    draw_vertical_gradient(WIN, (20, 40, 30), (10, 20, 15))
    update_pulse(3, 50)
    glow_col = (255, 220 - pulse_value//2, 120)
    draw_text_centered(WIN, "🎉 Congratulations! 🎉", 90, FONT, glow_col)
    draw_text_centered(WIN, f"Your Time: {get_elapsed_time()}", 150, SMALL_FONT, (220, 230, 255))

    play_again_btn=pygame.Rect(WIDTH//2-110, 240, 220, 60)
    menu_btn=pygame.Rect(WIDTH//2-110, 330, 220, 60)
    draw_button(WIN, play_again_btn, "Play Again", "win_again", base_color=(100,80,180), hover_color=(160,120,240))
    draw_button(WIN, menu_btn, "Main Menu", "win_menu", base_color=(180,80,100), hover_color=(240,120,160))

    pygame.display.update()
    return play_again_btn,menu_btn


def draw_lost_screen():
    draw_vertical_gradient(WIN, (40, 20, 20), (20, 10, 10))
    update_pulse(3, 50)
    glow_col = (255, 100 + pulse_value//2, 100)
    draw_text_centered(WIN, "❌ Incorrect Solution! ❌", 90, FONT, glow_col)
    draw_text_centered(WIN, f"Your Time: {get_elapsed_time()}", 150, SMALL_FONT, (240, 200, 200))

    play_again_btn = pygame.Rect(WIDTH//2-110, 240, 220, 60)
    menu_btn = pygame.Rect(WIDTH//2-110, 330, 220, 60)
    draw_button(WIN, play_again_btn, "Try Again", "lost_again", base_color=(200, 80, 80), hover_color=(255, 120, 120))
    draw_button(WIN, menu_btn, "Main Menu", "lost_menu", base_color=(120, 80, 200), hover_color=(160, 120, 255))

    pygame.display.update()
    return play_again_btn, menu_btn


def main():
    global current_screen, selected_cell, active_input, input_text, login_message, selected_difficulty, current_user, start_time
    clock = pygame.time.Clock()
    history_screen_open=False

    # to catch ENTER on login
    username_box = password_box = login_btn = reg_btn = None
    buttons = {}
    play_again_btn = menu_btn = None

    while True:
        clock.tick(60)


        if current_screen=="login":
            username_box, password_box, login_btn, reg_btn = draw_login_screen()
        elif current_screen=="home":
            buttons = draw_menu()
        elif current_screen=="history" and history_screen_open:
            draw_history_screen(current_user)
        elif current_screen=="game":
            draw_game()
            # ---- UPDATED: finish game on full board (win or lost) ---- #
            if all(0 not in row for row in grid):  # board is fully filled
                elapsed_time = int(time.time() - start_time)
                if is_board_complete_and_valid(grid):
                    flash_completed_board()
                    update_stats(current_user, selected_difficulty, True, elapsed_time)
                    play_win()
                    current_screen = "win"
                else:
                    update_stats(current_user, selected_difficulty, False, elapsed_time)
                    play_lose()
                    current_screen = "lost"
        elif current_screen=="win":
            play_again_btn, menu_btn = draw_win_screen()
        elif current_screen=="lost":
            play_again_btn, menu_btn = draw_lost_screen()

        # --- EVENTS --- #
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                save_users()
                pygame.quit()
                sys.exit()

            # --- Login --- #
            if current_screen=="login":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if username_box and username_box.collidepoint(event.pos):
                        active_input="username"
                    elif password_box and password_box.collidepoint(event.pos):
                        active_input="password"
                    elif login_btn and login_btn.collidepoint(event.pos):
                        press_button("login_btn")
                        user=input_text["username"].strip()
                        pwd=input_text["password"].strip()
                        if user=="" or pwd=="":
                            login_message="Username/password cannot be empty!"
                        elif user not in users:
                            login_message="Username does not exist!"
                        elif users[user]["password"]!=pwd:
                            login_message="Incorrect password!"
                        else:
                            current_user=user
                            current_screen="home"
                            login_message=""
                            input_text={"username":"","password":""}
                    elif reg_btn and reg_btn.collidepoint(event.pos):
                        press_button("reg_btn")
                        user=input_text["username"].strip()
                        pwd=input_text["password"].strip()
                        if len(user)<3:
                            login_message="Username must be at least 3 chars!"
                        elif len(pwd)<5:
                            login_message="Password must be at least 5 chars!"
                        elif user in users:
                            login_message="Username already exists!"
                        else:
                            users[user]={"password":pwd,"stats":{"Easy":{"played":0,"won":0,"lost":0,"best_time":None},"Medium":{"played":0,"won":0,"lost":0,"best_time":None},"Hard":{"played":0,"won":0,"lost":0,"best_time":None}}}
                            save_users()
                            login_message="Registered! Please login."
                            input_text={"username":"","password":""}

                # Keyboard on login
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_TAB:
                        active_input="password" if active_input=="username" else "username"
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        # act like clicking Login
                        if login_btn:
                            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'pos': (login_btn.centerx, login_btn.centery), 'button':1}))
                    elif event.key==pygame.K_BACKSPACE:
                        input_text[active_input]=input_text[active_input][:-1]
                    else:
                        if event.unicode.isprintable():
                            input_text[active_input]+=event.unicode

            elif current_screen=="home":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    for level,btn in buttons.items():
                        if btn.collidepoint(event.pos):
                            press_button(f"menu_{'history' if level=='History' else level}")
                            if level=="History":
                                current_screen="history"
                                history_screen_open=True
                            else:
                                selected_difficulty=level
                                load_puzzle(level)
                                current_screen="game"
                                selected_cell=(-1,-1)

            elif current_screen=="history":
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        current_screen="home"

            elif current_screen=="game":
                if event.type==pygame.KEYDOWN:
                    if event.key==pygame.K_ESCAPE:
                        current_screen="home"
                    elif selected_cell!=(-1,-1):
                        row,col=selected_cell
                        if original_grid[row][col]==0:
                            # editing keys
                            if event.key in [pygame.K_BACKSPACE,pygame.K_DELETE, pygame.K_0, pygame.K_KP0]:
                                grid[row][col]=0
                            elif pygame.K_1<=event.key<=pygame.K_9:
                                grid[row][col]=event.key-pygame.K_0
                            elif pygame.K_KP1<=event.key<=pygame.K_KP9:
                                grid[row][col]=event.key-pygame.K_KP0

                            # advance selection only when Enter/Tab pressed AND the cell currently has a number
                            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_TAB):
                                if grid[row][col] != 0 and original_grid[row][col] == 0:
                                    selected_cell = move_to_next_editable_cell(row, col)
                elif event.type==pygame.MOUSEBUTTONDOWN:
                    x,y=event.pos
                    # limit clicks to board area using aligned geometry
                    if BOARD_X <= x <= BOARD_X + BOARD_SIZE and BOARD_Y <= y <= BOARD_Y + BOARD_SIZE:
                        row=(y-BOARD_Y)//CELL_SIZE
                        col=(x-BOARD_X)//CELL_SIZE
                        selected_cell=(row,col)

            elif current_screen=="win":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if play_again_btn and play_again_btn.collidepoint(event.pos):
                        press_button("win_again")
                        load_puzzle(selected_difficulty)
                        current_screen="game"
                    elif menu_btn and menu_btn.collidepoint(event.pos):
                        press_button("win_menu")
                        current_screen="home"

            elif current_screen=="lost":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if play_again_btn and play_again_btn.collidepoint(event.pos):
                        press_button("lost_again")
                        load_puzzle(selected_difficulty)
                        current_screen="game"
                    elif menu_btn and menu_btn.collidepoint(event.pos):
                        press_button("lost_menu")
                        current_screen="home"

if __name__=="__main__":
    main()
