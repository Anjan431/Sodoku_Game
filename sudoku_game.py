# sudoku_game.py
import time

import pygame
from solver import solve, is_valid

pygame.init()

WIDTH, HEIGHT = 540, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

font = pygame.font.SysFont("comicsans", 40)
small_font = pygame.font.SysFont("comicsans", 24)
# Predefined puzzles
easy_puzzle = [
    [0, 0, 3, 0, 2, 0, 6, 0, 0],
    [9, 0, 0, 3, 0, 5, 0, 0, 1],
    [0, 0, 1, 8, 0, 6, 4, 0, 0],
    [0, 0, 8, 1, 0, 2, 9, 0, 0],
    [7, 0, 0, 0, 0, 0, 0, 0, 8],
    [0, 0, 6, 7, 0, 8, 2, 0, 0],
    [0, 0, 2, 6, 0, 9, 5, 0, 0],
    [8, 0, 0, 2, 0, 3, 0, 0, 9],
    [0, 0, 5, 0, 1, 0, 3, 0, 0]
]

medium_puzzle = [
    [0, 0, 0, 0, 6, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 9, 0],
    [0, 0, 0, 0, 0, 4, 2, 0, 0],
    [0, 0, 0, 0, 5, 9, 0, 0, 8],
    [0, 0, 7, 0, 0, 0, 1, 0, 0],
    [5, 0, 0, 7, 3, 0, 0, 0, 0],
    [0, 0, 3, 5, 0, 0, 0, 0, 0],
    [0, 5, 0, 0, 0, 3, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0]
]

hard_puzzle = [
    [0, 0, 0, 6, 0, 0, 4, 0, 0],
    [7, 0, 0, 0, 0, 3, 6, 0, 0],
    [0, 0, 0, 0, 9, 1, 0, 8, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 5, 0, 1, 8, 0, 0, 0, 3],
    [0, 0, 0, 3, 0, 6, 0, 4, 5],
    [0, 4, 0, 2, 0, 0, 0, 6, 0],
    [9, 0, 3, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 1, 0, 0]
]

# Sample Sudoku puzzle (0 = empty)
grid = [
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

original_grid = [row[:] for row in grid]  # Save original

selected = None

def draw_grid(win):
    gap = WIDTH // 9
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(win, (0, 0, 0), (0, i * gap), (WIDTH, i * gap), thickness)
        pygame.draw.line(win, (0, 0, 0), (i * gap, 0), (i * gap, WIDTH), thickness)

def draw_numbers(win):
    gap = WIDTH // 9
    for i in range(9):
        for j in range(9):
            num = grid[i][j]
            if num != 0:
                color = (0, 0, 0) if original_grid[i][j] != 0 else (50, 50, 255)
                text = font.render(str(num), 1, color)
                win.blit(text, (j * gap + 18, i * gap + 15))

def highlight_cell(win, row, col):
    gap = WIDTH // 9
    pygame.draw.rect(win, (180, 180, 255), (col * gap, row * gap, gap, gap))

def redraw_window(win, start_time):
    win.fill((255, 255, 255))
    if selected:
        highlight_cell(win, selected[0], selected[1])
    draw_numbers(win)
    draw_grid(win)

    # Draw instructions
    text = small_font.render("Enter = Solve | Backspace = Delete", 1, (0, 0, 0))
    win.blit(text, (10, WIDTH + 10))

    # Draw timer
    elapsed = int(time.time() - start_time)
    minutes = elapsed // 60
    seconds = elapsed % 60
    timer_text = small_font.render(f"Time: {minutes:02}:{seconds:02}", 1, (0, 0, 0))
    win.blit(timer_text, (WIDTH - 130, WIDTH + 10))

def get_clicked_pos(pos):
    if pos[0] < WIDTH and pos[1] < WIDTH:
        gap = WIDTH // 9
        x = pos[0] // gap
        y = pos[1] // gap
        return (y, x)
    return None
def game_loop():
    while True:
        puzzle = select_difficulty()
        main(puzzle)

def select_difficulty():
    back_rect = pygame.Rect(WIDTH//2 - 50, 350, 100, 40)  # x, y, width, height

    while True:
        WIN.fill((255, 255, 255))
        title = font.render("Select Difficulty", True, (0, 0, 0))
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        easy_text = small_font.render("1. Easy", True, (0, 128, 0))
        med_text = small_font.render("2. Medium", True, (255, 165, 0))
        hard_text = small_font.render("3. Hard", True, (255, 0, 0))

        WIN.blit(easy_text, (WIDTH // 2 - 40, 200))
        WIN.blit(med_text, (WIDTH // 2 - 40, 240))
        WIN.blit(hard_text, (WIDTH // 2 - 40, 280))

        # Draw Back button
        pygame.draw.rect(WIN, (180, 180, 180), back_rect)
        back_text = small_font.render("Back", True, (0, 0, 0))
        WIN.blit(back_text, (back_rect.x + 25, back_rect.y + 7))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return easy_puzzle
                elif event.key == pygame.K_2:
                    return medium_puzzle
                elif event.key == pygame.K_3:
                    return hard_puzzle

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if back_rect.collidepoint(pos):
                    # Here you can decide what "Back" does
                    # For example, exit or go to a main menu (if you have one)
                    pygame.quit()
                    exit()

                    def game_loop():
                        while True:
                            puzzle = select_difficulty()
                            main(puzzle)


def main(puzzle):
    global grid, original_grid, selected
    selected = None
    grid = [row[:] for row in puzzle]
    original_grid = [row[:] for row in grid]
    start_time = time.time()

    run = True
    while run:
        redraw_window(WIN, start_time)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if selected:
                    row, col = selected
                    if original_grid[row][col] == 0:
                        if pygame.K_1 <= event.key <= pygame.K_9:
                            grid[row][col] = event.key - pygame.K_0
                        elif event.key in [pygame.K_BACKSPACE, pygame.K_DELETE]:
                            grid[row][col] = 0
                        elif event.key == pygame.K_RETURN:
                            solve(grid)

                # Press ESC to go back to level selection
                if event.key == pygame.K_ESCAPE:
                    run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                selected = get_clicked_pos(pos)

def start_game():
    game_loop()

if __name__ == "__main__":
    start_game()
