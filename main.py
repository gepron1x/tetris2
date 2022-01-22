# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys

import pygame
import pygame_gui
from pygame.sprite import Sprite, AbstractGroup

from event import Signal

WIDTH, HEIGHT = 600, 600

BOX_SIZE = 50

GT = 9.8

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


class CellSprite(pygame.sprite.Sprite):

    def __init__(self, *groups: AbstractGroup):
        super().__init__(*groups)


class BrickSprite(pygame.sprite.Sprite):
    IMAGE = load_image("bricks.png")

    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = BrickSprite.IMAGE
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x, self.rect.y = pos


class Figure(pygame.sprite.Sprite):
    IMAGE = load_image("box.png")

    def __init__(self, pattern, pos, *groups: AbstractGroup):
        super().__init__(*groups)
        self.image = pygame.Surface((BOX_SIZE * len(pattern[0]), BOX_SIZE * len(pattern)), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        for i in range(len(pattern)):
            s = pattern[i]
            y = i * BOX_SIZE
            for j in range(len(s)):
                c = s[j]
                x = j * BOX_SIZE
                if c == 'B':
                    self.image.blit(Figure.IMAGE, (x, y))
        self.mask = pygame.mask.from_surface(self.image)

    def rotate(self, degrees):
        x, y = self.rect.x, self.rect.y
        self.image = pygame.transform.rotate(self.image, degrees)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.mask = pygame.mask.from_surface(self.image)


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

    def get_rect(self):
        return self.rect

    def set_rect(self, rect):
        self.rect = rect


class GameBoard:

    def __init__(self):
        self.all_sprites = pygame.sprite.Group()
        self.solid_sprites = pygame.sprite.Group()
        self.boxes = pygame.sprite.Group()

    def add_solid(self, sprite):
        self.all_sprites.add(sprite)
        self.solid_sprites.add(sprite)

    def add_box(self, box):
        self.add_solid(box)
        self.boxes.add(box)

    def collides_box(self, sprite):
        return pygame.sprite.spritecollideany(sprite, self.boxes)

    def update(self, *args, **kwargs):
        self.all_sprites.update(*args, **kwargs)

    def draw(self, screen):
        self.all_sprites.draw(screen)

    def collides_solid(self, sprite):
        for solid in self.solid_sprites:
            if pygame.sprite.collide_mask(sprite, solid):
                return True
        return False


class MovementController:
    def __init__(self, player: PlayerSprite, sprite_manager: GameBoard, step=10):
        self.sprite_manager = sprite_manager
        self.jumpCount = 0
        self.isJump = False

        self.player = player
        self.step = step
        self.jump = 0

    def handle(self):
        pressed = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        rect = self.player.get_rect()

        if pressed[pygame.K_a]:
            move_x -= self.step
        if pressed[pygame.K_d]:
            move_x += self.step
        if pressed[pygame.K_s]:
            move_y += self.step
        if pressed[pygame.K_w]:
            move_y -= self.step

        ''' if pressed[pygame.K_SPACE]:
            if self.jumpCount >= -10:
                neg = 1
                if self.jumpCount < 0:
                    neg = -1
                self.jump -= self.jumpCount ** 2 * 0.1 * neg
                move_y -= self.jump
                self.player.move(0, -self.jump)
                self.jumpCount -= 1
            else:
                self.isJump = False
                self.jumpCount = 10
        '''
        new_rect = rect.move(move_x, move_y)
        self.player.set_rect(new_rect)
        if self.sprite_manager.collides_solid(self.player):
            self.player.set_rect(rect)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        offset_x, offset_y = 0, 0

        if mouse_x > rect.x:
            offset_x += BOX_SIZE
        elif mouse_x < rect.x:
            offset_x -= BOX_SIZE

        if mouse_y > rect.y:
            offset_y += BOX_SIZE
        elif mouse_y < rect.y:
            offset_y -= BOX_SIZE

        if pressed[pygame.K_END]:
            x, y = pygame.mouse.get_pos()
            box = Figure(["B"], self.getboxpos(x, y))
            box.rotate(90)
            if not self.sprite_manager.collides_solid(box):
                self.sprite_manager.add_solid(box)

    def getboxpos(self, x, y):
        x_center = self.player.rect.x + self.player.image.get_width() // 2
        y_center = self.player.rect.y + self.player.image.get_height() // 2
        number_col = x_center // BOX_SIZE
        number_row = y_center // BOX_SIZE
        if x > self.player.rect.x and y > self.player.rect.y:
            if x > y:
                x_box, y_box = number_col * 50 + 50, number_row * 50
                return x_box, y_box
            else:
                x_box, y_box = number_col * 50, number_row * 50 + 50
                return x_box, y_box
        elif x > self.player.rect.x and y < self.player.rect.y:
            if x > y:
                x_box, y_box = number_col * 50 + 50, number_row * 50
                return x_box, y_box
            else:
                x_box, y_box = number_col * 50, number_row * 50 - 50
                return x_box, y_box
        elif x < self.player.rect.x and y > self.player.rect.y:
            if x > y:
                x_box, y_box = number_col * 50 - 50, number_row * 50
                return x_box, y_box
            else:
                x_box, y_box = number_col * 50, number_row * 50 + 50
                return x_box, y_box
        elif x < self.player.rect.x and y < self.player.rect.y:
            if x > y:
                x_box, y_box = number_col * 50 - 50, number_row * 50
                return x_box, y_box
            else:
                x_box, y_box = number_col * 50, number_row * 50 - 50
                return x_box, y_box


class TetrisGame:
    GRASS = pygame.transform.scale(load_image("grass.png"), (WIDTH, HEIGHT))

    def __init__(self, player: PlayerSprite, level, ui_manager: pygame_gui.UIManager):
        self.player = player
        self.ui_manager = ui_manager
        self.hello_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 275), (100, 50)),
                                                         text='Say Hello',
                                                         manager=ui_manager)

        self.sprite_manager = GameBoard()
        self.sprite_manager.all_sprites.add(player)
        self.sprite_manager.add_solid(Border(1, 1, WIDTH, 1))
        self.sprite_manager.add_solid(Border(1, HEIGHT - 1, WIDTH - 1, HEIGHT - 1))

        self.sprite_manager.add_solid(Border(1, 1, 1, HEIGHT - 1))
        self.sprite_manager.add_solid(Border(WIDTH - 1, 1, WIDTH - 1, HEIGHT - 1))

        for i in range(len(level)):
            s = level[i]
            y = i * BOX_SIZE
            for j in range(len(s)):
                c = s[j]
                x = j * BOX_SIZE
                if c == 'B':
                    self.sprite_manager.add_box(BrickSprite((x, y)))
        self.movement_control = MovementController(
            player, self.sprite_manager
        )

        def construct_ui():
            pass

    def update(self):
        self.movement_control.handle()
        self.sprite_manager.update()

    def draw(self, screen):
        screen.blit(TetrisGame.GRASS, (0, 0))

        self.sprite_manager.draw(screen)

    def handle_event(self, event):
        pass


def main():
    running = True
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))

    clock = pygame.time.Clock()
    player = PlayerSprite("player")
    page = TetrisGame(player, ["            ",
                               "            ",
                               "B        BBB",
                               "BB  B      B",
                               "BB        BB",
                               "B  B      BB",
                               "B  B  B BB  "], manager)
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            page.handle_event(event)
        manager.update(time_delta)
        page.update()
        page.draw(screen)
        manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(30)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
