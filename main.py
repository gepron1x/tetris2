# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys

import pygame
from pygame.sprite import Sprite

WIDTH, HEIGHT = 600, 600

BLUE_SKY = (51, 204, 255)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    print(fullname)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)

    return image


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2, *groups):
        super().__init__(*groups)
        if x1 == x2:  # вертикальная стенка
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class PlayerSprite(Sprite):
    IMAGE = load_image("character.png")

    def __init__(self, name, *groups):
        super().__init__(*groups)
        self.image = PlayerSprite.IMAGE
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - self.image.get_width() - 5
        self.rect.y = HEIGHT - self.image.get_height() - 5
        self.name = name

    def move(self, x, y):
        self.rect = self.rect.move(x, y)


class MovementController:
    def __init__(self, player, horizontal_borders, vertical_borders, step=10):
        self.vertical_borders = vertical_borders
        self.horizontal_borders = horizontal_borders

        self.player = player
        self.step = step

    def handle(self):
        pressed = pygame.key.get_pressed()
        move_x = 0

        if pressed[pygame.K_a]:
            move_x -= self.step
        if pressed[pygame.K_d]:
            move_x += self.step
        self.player.move(move_x, 0)


class TetrisGame:

    def __init__(self, player):
        self.all_sprites = pygame.sprite.Group()
        self.player = player
        vertical_borders = pygame.sprite.Group()
        vertical_borders.add(Border(5, 5, WIDTH - 5, 5, self.all_sprites),
                             Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5, self.all_sprites))
        horizontal_borders = pygame.sprite.Group()
        horizontal_borders.add(Border(5, 5, 5, HEIGHT - 5, self.all_sprites),
                               Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5, self.all_sprites))
        self.movement_control = MovementController(player, vertical_borders, horizontal_borders)
        self.all_sprites.add(player)

    def update(self):
        self.movement_control.handle()
        self.all_sprites.update()

    def draw(self, screen):
        screen.fill(BLUE_SKY)
        self.all_sprites.draw(screen)

    def handle_event(self, event):
        pass


def main():
    running = True
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    player = PlayerSprite("player")
    game = TetrisGame(player)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(30)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
