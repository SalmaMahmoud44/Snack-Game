import pygame
import sys
import time
import random
import numpy as np
import heapq

# Snake settings

frame_size_x = 720
frame_size_y = 480
difficulty = 20

pygame.init()
pygame.mixer.init()

pygame.display.set_caption('Snake Game')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
fps_controller = pygame.time.Clock()

white = (255, 255, 255)
red = (255, 50, 50)
green = (50, 255, 100)
dark_green = (6, 40, 0)
button_color = (10, 40, 60)
hover_color = (20, 60, 80)
bg_color = (10, 40, 50)

background = pygame.image.load('grass_template2.jpg')
background = pygame.transform.scale(background, (frame_size_x, frame_size_y))

eat_sound = pygame.mixer.Sound('pass.wav')
lose_sound = pygame.mixer.Sound('lose.wav')

apple_image = pygame.image.load('apple.png')
apple_image = pygame.transform.scale(apple_image, (30, 30))

class SnakeGame:
    def __init__(self):
        self.ai_algorithm = 'greedy'

    #show the text in screen
    def draw_text(self, text, font, color, surface, x, y, glow=False):
        if glow:
            glow_surface = font.render(text, True, (color[0], color[1], color[2]))
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                surface.blit(glow_surface, (x + dx, y + dy))
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))

    def create_button(self, surface, text, font, rect, base_color, hover_color, mouse_pos):
        color = hover_color if rect.collidepoint(mouse_pos) else base_color
        pygame.draw.rect(surface, color, rect, border_radius=8)
        text_surf = font.render(text, True, white)
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def show_score(self, score):
        score_font = pygame.font.SysFont('consolas', 20)
        score_surface = score_font.render('Score : ' + str(score), True, white)
        score_rect = score_surface.get_rect()
        score_rect.midtop = (frame_size_x / 10, 15)
        game_window.blit(score_surface, score_rect)

    def dist(self, state, goal):
        # Heuristic: Manhattan distance between two points
        return abs(goal[0] - state[0]) + abs(goal[1] - state[1])  # heuristic value

    def greedy(self, direction, pos, goal, body):
        directions = ['DOWN', 'UP', 'LEFT', 'RIGHT']
        moves = np.array([[0, 10], [0, -10], [-10, 0], [10, 0]])
        state_dict = {d: pos + m for d, m in zip(directions, moves)}
        distance_dict = {d: self.dist(pos + m, goal) for d, m in zip(directions, moves)}

        #see the body of Snake
        for d in directions.copy():
            if list(state_dict[d]) in body:
                directions.remove(d)

        #change direction
        change = direction
        if len(directions) == 0:
            return change
        if direction not in directions:
            change = directions[0]

        #search for shorter way
        for d in directions:
            if distance_dict[d] < distance_dict[change]:
                change = d

        return change

    def a_star(self, start, goal, body):
        moves = [(0, 10), (0, -10), (-10, 0), (10, 0)]
        open_set = [(0, start)]
        came_from = {}
        #store the actual value
        g_score = {tuple(start): 0}
        #store the evaluation function = actual + estimated
        f_score = {tuple(start): self.dist(start, goal)}
        body_set = set(tuple(b) for b in body)

        while open_set:
            _, current = heapq.heappop(open_set)

            #make sure we have arrived the goal
            if list(current) == list(goal):
                while tuple(current) != tuple(start):
                    prev = came_from[tuple(current)]
                    if tuple(prev) == tuple(start):
                        dx = current[0] - prev[0]
                        dy = current[1] - prev[1]
                        if dx == 10: return 'RIGHT'
                        if dx == -10: return 'LEFT'
                        if dy == 10: return 'DOWN'
                        if dy == -10: return 'UP'
                    current = prev

            for dx, dy in moves:
                #new position
                neighbor = (current[0] + dx, current[1] + dy)

                #check the body and wall avoids it to win
                if neighbor in body_set or not (0 <= neighbor[0] < frame_size_x and 0 <= neighbor[1] < frame_size_y):
                    continue

                tentative_g = g_score[tuple(current)] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self.dist(neighbor, goal)
                    f_score[neighbor] = f
                    heapq.heappush(open_set, (f, neighbor))

        return self.greedy('RIGHT', np.array(start), np.array(goal), body)

    def snake_game(self, mode='manual'):
        # Start position of the snake (initial state)
        snake_pos = [100, 50]
        snake_body = [[100, 50], [90, 50], [80, 50]]
        # Goal position (apple)
        # random position for apple
        food_pos = [random.randrange(1, (frame_size_x // 30)) * 30, random.randrange(1, (frame_size_y // 30)) * 30]
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
                if self.ai_algorithm == 'greedy':
                    change_to = self.greedy(direction, np.array(snake_pos), np.array(food_pos), snake_body)
                elif self.ai_algorithm == 'astar':
                    change_to = self.a_star(snake_pos, food_pos, snake_body)

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

            #add head
            snake_body.insert(0, list(snake_pos))

            snake_head_rect = pygame.Rect(snake_pos[0], snake_pos[1], 10, 10)
            apple_rect = pygame.Rect(food_pos[0], food_pos[1], 30, 30)

            #check if snake ate apple
            if snake_head_rect.colliderect(apple_rect):
                score += 1
                food_spawn = False
                if eat_sound:
                    eat_sound.play()
                speed += 1
            else:
                snake_body.pop()

            if not food_spawn:
                food_pos = [random.randrange(1, (frame_size_x // 30)) * 30, random.randrange(1, (frame_size_y // 30)) * 30]
            food_spawn = True

            game_window.blit(background, (0, 0))
            #draw body of snake
            for pos in snake_body:
                pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

            # draw apple
            game_window.blit(apple_image, (food_pos[0], food_pos[1]))

            for block in snake_body[1:]:
                if snake_pos == block:
                    game_over_flag = True

            self.show_score(score)
            pygame.display.update()

            if game_over_flag:
                if lose_sound:
                    lose_sound.play()
                time.sleep(1)
                self.game_over_screen()

            fps_controller.tick(speed)

    def game_over_screen(self):
        font_big = pygame.font.SysFont('Arial', 60, bold=True)
        font_small = pygame.font.SysFont('Arial', 30)

        while True:
            mouse_pos = pygame.mouse.get_pos()
            game_window.blit(background, (0, 0))

            self.draw_text('YOU LOST!', font_big, red, game_window, frame_size_x // 2 - 150, 100, glow=True)

            main_menu_button = pygame.Rect(frame_size_x // 2 - 150, 220, 300, 50)
            exit_button = pygame.Rect(frame_size_x // 2 - 150, 300, 300, 50)

            self.create_button(game_window, 'Main Menu', font_small, main_menu_button, button_color, hover_color, mouse_pos)
            self.create_button(game_window, 'Exit', font_small, exit_button, button_color, hover_color, mouse_pos)

            pygame.display.update()

            for event in pygame.event.get():
                #when I close the game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                #when I click any button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if main_menu_button.collidepoint(mouse_pos):
                        self.main_menu()
                    if exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

    def main_menu(self):
        font_big = pygame.font.SysFont('Arial', 60, bold=True)
        font_small = pygame.font.SysFont('Arial', 30)

        while True:
            mouse_pos = pygame.mouse.get_pos()
            game_window.blit(background, (0, 0))

            self.draw_text('Snake Game', font_big, green, game_window, frame_size_x // 2 - 170, 100, glow=True)

            manual_button = pygame.Rect(frame_size_x // 2 - 150, 220, 300, 50)
            ai_greedy_button = pygame.Rect(frame_size_x // 2 - 150, 300, 300, 50)
            ai_astar_button = pygame.Rect(frame_size_x // 2 - 150, 360, 300, 50)
            exit_button = pygame.Rect(frame_size_x // 2 - 150, 420, 300, 50)

            self.create_button(game_window, 'Manual Mode', font_small, manual_button, button_color, hover_color, mouse_pos)
            self.create_button(game_window, 'AI Mode (Greedy)', font_small, ai_greedy_button, button_color, hover_color, mouse_pos)
            self.create_button(game_window, 'AI Mode (A*)', font_small, ai_astar_button, button_color, hover_color, mouse_pos)
            self.create_button(game_window, 'Exit', font_small, exit_button, button_color, hover_color, mouse_pos)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if manual_button.collidepoint(mouse_pos):
                        self.snake_game(mode='manual')
                    if ai_greedy_button.collidepoint(mouse_pos):
                        self.ai_algorithm = 'greedy'
                        self.snake_game(mode='ai')
                    if ai_astar_button.collidepoint(mouse_pos):
                        self.ai_algorithm = 'astar'
                        self.snake_game(mode='ai')
                    if exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

if __name__ == "__main__":
    game = SnakeGame()
    game.main_menu()
