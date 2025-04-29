import pygame
import sys
import time
import random
import numpy as np

# Window size
frame_size_x = 720
frame_size_y = 480

# Difficulty (snake speed)
difficulty = 20

# Initialize pygame
pygame.init()
pygame.mixer.init()

pygame.display.set_caption('Snake Game')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
fps_controller = pygame.time.Clock()

# Colors
white = (255, 255, 255)
red = (255, 50, 50)
green = (50, 255, 100)
dark_green = (6, 40, 0)
button_color = (10, 40, 60)
hover_color = (20, 60, 80)
bg_color = (10, 40, 50)

# Load background image
background = pygame.image.load('grass_template2.jpg')
background = pygame.transform.scale(background, (frame_size_x, frame_size_y))

# Load sounds
eat_sound = pygame.mixer.Sound('pass.wav')
lose_sound = pygame.mixer.Sound('lose.wav')

# Load apple image and resize
apple_image = pygame.image.load('apple.png')
apple_image = pygame.transform.scale(apple_image, (30, 30))


def draw_text(text, font, color, surface, x, y, glow=False):
    if glow:
        glow_surface = font.render(text, True, (color[0], color[1], color[2]))
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            surface.blit(glow_surface, (x + dx, y + dy))
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, (x, y))


def create_button(surface, text, font, rect, base_color, hover_color, mouse_pos):
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(surface, color, rect, border_radius=8)
    text_surf = font.render(text, True, white)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)


def show_score(score):
    score_font = pygame.font.SysFont('consolas', 20)
    score_surface = score_font.render('Score : ' + str(score), True, white)
    score_rect = score_surface.get_rect()
    score_rect.midtop = (frame_size_x / 10, 15)
    game_window.blit(score_surface, score_rect)


def dist(state, goal):
    return abs(goal[0] - state[0]) + abs(goal[1] - state[1])


def greedy(direction, pos, goal, body):
    directions = ['DOWN', 'UP', 'LEFT', 'RIGHT']
    moves = np.array([[0, 10], [0, -10], [-10, 0], [10, 0]])
    state_dict = {d: pos + m for d, m in zip(directions, moves)}
    distance_dict = {d: dist(pos + m, goal) for d, m in zip(directions, moves)}

    for d in directions.copy():
        if list(state_dict[d]) in body:
            directions.remove(d)

    change = direction
    if len(directions) == 0:
        return change
    if direction not in directions:
        change = directions[0]

    for d in directions:
        if distance_dict[d] < distance_dict[change]:
            change = d

    return change


def snake_game(mode='manual'):
    snake_pos = [100, 50]
    snake_body = [[100, 50], [90, 50], [80, 50]]
    food_pos = [random.randrange(1, (frame_size_x // 30)) * 30,
                random.randrange(1, (frame_size_y // 30)) * 30]
    food_spawn = True
    direction = 'RIGHT'
    change_to = direction
    score = 0
    game_over_flag = False
    speed = difficulty

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if mode == 'manual':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and direction != 'DOWN':
                        change_to = 'UP'
                    if event.key == pygame.K_DOWN and direction != 'UP':
                        change_to = 'DOWN'
                    if event.key == pygame.K_LEFT and direction != 'RIGHT':
                        change_to = 'LEFT'
                    if event.key == pygame.K_RIGHT and direction != 'LEFT':
                        change_to = 'RIGHT'

        if mode == 'ai':
            change_to = greedy(direction, np.array(snake_pos), np.array(food_pos), snake_body)

        direction = change_to

        if direction == 'UP':
            snake_pos[1] -= 10
        if direction == 'DOWN':
            snake_pos[1] += 10
        if direction == 'LEFT':
            snake_pos[0] -= 10
        if direction == 'RIGHT':
            snake_pos[0] += 10

        if snake_pos[0] < 0 or snake_pos[0] > frame_size_x - 10 or snake_pos[1] < 0 or snake_pos[1] > frame_size_y - 10:
            game_over_flag = True

        snake_body.insert(0, list(snake_pos))

        snake_head_rect = pygame.Rect(snake_pos[0], snake_pos[1], 10, 10)
        apple_rect = pygame.Rect(food_pos[0], food_pos[1], 30, 30)

        if snake_head_rect.colliderect(apple_rect):
            score += 1
            food_spawn = False
            eat_sound.play()
            speed += 1
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = [random.randrange(1, (frame_size_x // 30)) * 30,
                        random.randrange(1, (frame_size_y // 30)) * 30]
        food_spawn = True

        game_window.blit(background, (0, 0))

        for pos in snake_body:
            pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

        game_window.blit(apple_image, (food_pos[0], food_pos[1]))

        for block in snake_body[1:]:
            if snake_pos == block:
                game_over_flag = True

        show_score(score)
        pygame.display.update()

        if game_over_flag:
            lose_sound.play()  # تشغيل صوت الخسارة
            time.sleep(1)
            game_over_screen()

        fps_controller.tick(speed)


def game_over_screen():
    font_big = pygame.font.SysFont('Arial', 60, bold=True)
    font_small = pygame.font.SysFont('Arial', 30)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        game_window.blit(background, (0, 0))

        draw_text('YOU LOST!', font_big, red, game_window, frame_size_x // 2 - 150, 100, glow=True)

        main_menu_button = pygame.Rect(frame_size_x // 2 - 150, 220, 300, 50)
        exit_button = pygame.Rect(frame_size_x // 2 - 150, 300, 300, 50)

        create_button(game_window, 'Main Menu', font_small, main_menu_button, button_color, hover_color, mouse_pos)
        create_button(game_window, 'Exit', font_small, exit_button, button_color, hover_color, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if main_menu_button.collidepoint(mouse_pos):
                    main_menu()
                if exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()


def main_menu():
    font_big = pygame.font.SysFont('Arial', 60, bold=True)
    font_small = pygame.font.SysFont('Arial', 30)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        game_window.blit(background, (0, 0))

        draw_text('Snake Game', font_big, green, game_window, frame_size_x // 2 - 170, 100, glow=True)

        manual_button = pygame.Rect(frame_size_x // 2 - 150, 220, 300, 50)
        ai_button = pygame.Rect(frame_size_x // 2 - 150, 300, 300, 50)
        exit_button = pygame.Rect(frame_size_x // 2 - 150, 380, 300, 50)

        create_button(game_window, 'Manual Mode', font_small, manual_button, button_color, hover_color, mouse_pos)
        create_button(game_window, 'AI Mode', font_small, ai_button, button_color, hover_color, mouse_pos)
        create_button(game_window, 'Exit', font_small, exit_button, button_color, hover_color, mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if manual_button.collidepoint(mouse_pos):
                    snake_game(mode='manual')
                if ai_button.collidepoint(mouse_pos):
                    snake_game(mode='ai')
                if exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()


if __name__ == "__main__":
    main_menu()
