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
FONT = pygame.font.SysFont("comicsans", 40)
SMALL_FONT = pygame.font.SysFont("comicsans", 30)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
GREEN = (0, 150, 0)
RED = (255, 0, 0)

# ---------------- Game State ---------------- #
current_screen = "login"
selected_cell = (-1, -1)
grid = [[0]*9 for _ in range(9)]
original_grid = None
start_time = None
selected_difficulty = None

# Login System
users = {}  # Loaded from JSON
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

    # Ensure stats structure exists for all users
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
save_users()  # ensure file exists

# ---------------- Helper Functions ---------------- #
def draw_text_centered(surface, text, y, font, color=BLACK):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (WIDTH//2 - rendered.get_width()//2, y))

def draw_grid():
    for i in range(GRID_SIZE+1):
        lw = 3 if i%3 == 0 else 1
        pygame.draw.line(WIN, BLACK, (0, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), lw)
        pygame.draw.line(WIN, BLACK, (i*CELL_SIZE, 0), (i*CELL_SIZE, WIDTH), lw)

def draw_numbers():
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            num = grid[i][j]
            if num != 0:
                color = BLACK if original_grid[i][j] != 0 else BLUE
                text = FONT.render(str(num), True, color)
                WIN.blit(text, (j*CELL_SIZE+20, i*CELL_SIZE+10))

def draw_selected_cell():
    if selected_cell != (-1, -1):
        row, col = selected_cell
        pygame.draw.rect(WIN, BLUE, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

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

# ---------------- Sudoku Logic ---------------- #
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

def flash_completed_board():
    for _ in range(3):
        WIN.fill(WHITE)
        draw_grid()
        draw_numbers()
        pygame.display.update()
        pygame.time.delay(300)
        WIN.fill(WHITE)
        draw_grid()
        pygame.display.update()
        pygame.time.delay(300)

# ---------------- Screens ---------------- #
def draw_login_screen():
    WIN.fill(WHITE)
    draw_text_centered(WIN,"Sudoku Login/Register",50,FONT)
    username_box = pygame.Rect(WIDTH//2-100,150,200,50)
    password_box = pygame.Rect(WIDTH//2-100,250,200,50)
    login_btn = pygame.Rect(WIDTH//2-120,350,100,50)
    reg_btn = pygame.Rect(WIDTH//2+20,350,100,50)
    pygame.draw.rect(WIN,GRAY,username_box)
    pygame.draw.rect(WIN,GRAY,password_box)
    pygame.draw.rect(WIN,GRAY,login_btn)
    pygame.draw.rect(WIN,GRAY,reg_btn)
    WIN.blit(SMALL_FONT.render(input_text["username"], True, BLACK), (username_box.x+10, username_box.y+10))
    pwd_display="*"*len(input_text["password"])
    WIN.blit(SMALL_FONT.render(pwd_display, True, BLACK),(password_box.x+10,password_box.y+10))
    draw_text_centered(WIN,"Username",105,SMALL_FONT)
    draw_text_centered(WIN,"Password",205,SMALL_FONT)
    WIN.blit(SMALL_FONT.render("Login", True, BLACK), (login_btn.x+15,login_btn.y+10))
    WIN.blit(SMALL_FONT.render("Register", True, BLACK), (reg_btn.x+5,login_btn.y+10))
    if login_message:
        draw_text_centered(WIN,login_message,420,SMALL_FONT,RED)
    pygame.display.update()
    return username_box,password_box,login_btn,reg_btn

def draw_menu():
    WIN.fill(WHITE)
    draw_text_centered(WIN,"Select Difficulty",50,FONT)
    buttons={}
    for idx,level in enumerate(["Easy","Medium","Hard"]):
        btn = pygame.Rect(WIDTH//2-80,150+idx*100,160,60)
        pygame.draw.rect(WIN,GRAY,btn)
        WIN.blit(SMALL_FONT.render(level,True,BLACK),(btn.x+40,btn.y+15))
        buttons[level]=btn
    history_btn = pygame.Rect(WIDTH//2-80,500,160,50)
    pygame.draw.rect(WIN,GRAY,history_btn)
    WIN.blit(SMALL_FONT.render("History",True,BLACK),(history_btn.x+30,history_btn.y+10))
    pygame.display.update()
    buttons["History"]=history_btn
    return buttons

def draw_history_screen(username):
    WIN.fill(WHITE)
    draw_text_centered(WIN, f"{username}'s History", 50, FONT)
    y_start = 120
    for level in ["Easy", "Medium", "Hard"]:
        stats = users[username]["stats"].get(level, {"played":0,"won":0,"lost":0,"best_time":None})
        draw_text_centered(WIN, f"{level}:", y_start, SMALL_FONT, BLACK)
        draw_text_centered(WIN, f"Played: {stats['played']}, Won: {stats['won']}, Lost: {stats['lost']}", y_start+30, SMALL_FONT)
        best_time = stats.get("best_time")
        if best_time:
            minutes = best_time // 60
            seconds = best_time % 60
            draw_text_centered(WIN, f"Best Time: {minutes:02}:{seconds:02}", y_start+60, SMALL_FONT)
        y_start += 100
    draw_text_centered(WIN, "Press ESC to return", 500, SMALL_FONT)
    pygame.display.update()

def draw_game():
    WIN.fill(WHITE)
    draw_grid()
    draw_numbers()
    draw_selected_cell()
    timer_text=SMALL_FONT.render("Time: "+get_elapsed_time(), True,BLACK)
    WIN.blit(timer_text,(20,HEIGHT-40))
    pygame.display.update()

def draw_win_screen():
    WIN.fill(WHITE)
    draw_text_centered(WIN,"🎉 Congratulations! 🎉",80,FONT,GREEN)
    draw_text_centered(WIN,f"Your Time: {get_elapsed_time()}",150,SMALL_FONT,BLACK)
    play_again_btn=pygame.Rect(WIDTH//2-100,250,200,60)
    menu_btn=pygame.Rect(WIDTH//2-100,350,200,60)
    pygame.draw.rect(WIN,GRAY,play_again_btn)
    pygame.draw.rect(WIN,GRAY,menu_btn)
    WIN.blit(SMALL_FONT.render("Play Again",True,BLACK),(play_again_btn.x+40,play_again_btn.y+15))
    WIN.blit(SMALL_FONT.render("Main Menu",True,BLACK),(menu_btn.x+40,menu_btn.y+15))
    pygame.display.update()
    return play_again_btn,menu_btn

# ---------------- Main Loop ---------------- #
def main():
    global current_screen, selected_cell, active_input, input_text, login_message, selected_difficulty, current_user, start_time
    clock = pygame.time.Clock()
    history_screen_open=False

    while True:
        clock.tick(60)

        if current_screen=="login":
            username_box,password_box,login_btn,reg_btn=draw_login_screen()
        elif current_screen=="home":
            buttons=draw_menu()
        elif current_screen=="history" and history_screen_open:
            draw_history_screen(current_user)
        elif current_screen=="game":
            draw_game()
            if is_board_complete_and_valid(grid):
                elapsed_time=int(time.time()-start_time)
                flash_completed_board()
                update_stats(current_user, selected_difficulty, True, elapsed_time)
                current_screen="win"
        elif current_screen=="win":
            play_again_btn,menu_btn=draw_win_screen()

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                save_users()
                pygame.quit()
                sys.exit()

            # --- Login ---
            if current_screen=="login":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    if username_box.collidepoint(event.pos):
                        active_input="username"
                    elif password_box.collidepoint(event.pos):
                        active_input="password"
                    elif login_btn.collidepoint(event.pos):
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
                    elif reg_btn.collidepoint(event.pos):
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

            elif current_screen=="home":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    for level,btn in buttons.items():
                        if btn.collidepoint(event.pos):
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
                            if event.key in [pygame.K_BACKSPACE,pygame.K_DELETE]:
                                grid[row][col]=0
                            elif pygame.K_1<=event.key<=pygame.K_9:
                                grid[row][col]=event.key-pygame.K_0
                elif event.type==pygame.MOUSEBUTTONDOWN:
                    x,y=event.pos
                    if y<WIDTH:
                        row=y//CELL_SIZE
                        col=x//CELL_SIZE
                        selected_cell=(row,col)

            elif current_screen=="win":
                if event.type==pygame.MOUSEBUTTONDOWN:
                    x,y=event.pos
                    if play_again_btn.collidepoint(event.pos):
                        load_puzzle(selected_difficulty)
                        current_screen="game"
                    elif menu_btn.collidepoint(event.pos):
                        current_screen="home"

            # --- Text input ---
            if event.type==pygame.KEYDOWN and current_screen=="login":
                if event.key==pygame.K_TAB:
                    active_input="password" if active_input=="username" else "username"
                elif event.key==pygame.K_BACKSPACE:
                    input_text[active_input]=input_text[active_input][:-1]
                elif event.unicode.isprintable():
                    input_text[active_input]+=event.unicode

if __name__=="__main__":
    main()
