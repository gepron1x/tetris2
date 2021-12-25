# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys

import pygame
from pygame.sprite import Sprite, AbstractGroup

from event import Signal

WIDTH, HEIGHT = 600, 600

BLUE_SKY = (51, 204, 255)


def as_rgb(color):
    return color.r, color.g, color.b


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


class Page:

    def update(self):
        pass

    def handle_event(self, event):
        pass

    def draw(self, screen):
        pass


class ButtonSprite(Sprite):

    def __init__(self, pos, text, font, color, *groups: AbstractGroup):
        super().__init__(*groups)
        self.text = text
        self.font = font
        rendered_text = font.render(self.text, True, (0, 0, 0))
        self.image = pygame.Surface((rendered_text.get_rect().width + 6, rendered_text.get_rect().height + 6))
        self.image.fill(as_rgb(color))
        self.image.blit(rendered_text, (3, 3))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.pressed = Signal()

    def press(self):
        self.pressed.emit()


class MainPage(Page):
    # BACKGROUND = load_image("background.png")
    LEVELS, STATISTICS = 0, 1

    def __init__(self):
        self.levels = Signal()
        self.buttons = pygame.sprite.Group()
        levels = ButtonSprite((WIDTH // 2 - 100, 400), "Уровни", pygame.font.Font(None, 50),
                              pygame.color.Color('white'), self.buttons)
        levels.pressed.connect(lambda: self.levels.emit())

        statistics = ButtonSprite((WIDTH // 2 - 100, 450), "Статистика", pygame.font.Font(None, 50),
                                  pygame.color.Color('white'), self.buttons)
        statistics.pressed.connect(lambda: self.statistics.emit())
        self.statistics = Signal()
        self.chosen = MainPage.LEVELS

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.click(event.pos)

    def draw(self, screen):
        screen.fill(BLUE_SKY)
        self.buttons.draw(screen)

    def click(self, pos):
        for button in self.buttons.sprites():
            if button.rect.collidepoint(*pos):
                button.press()


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
    page = MainPage()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            page.handle_event(event)
        page.update()
        page.draw(screen)
        pygame.display.flip()
        clock.tick(30)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
