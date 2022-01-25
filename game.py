import datetime

import pygame
import pygame_gui
from pygame.sprite import AbstractGroup, Sprite

from page import Page
from util import load_image, HEIGHT, WIDTH, BOX_SIZE

FIRST_FIGURE = ["B  ",
                "BBB"]
SECOND_FIGURE = ["  B",
                 "BBB"]
THIRD_FIGURE = ["B",
                "B ",
                "BB"]
FOURTH_FIGURE = ["BB",
                 "B ",
                 "B "]


class Level:
    def __init__(self, name, description, content):
        self.name = name
        self.description = description
        self.content = content

    def get_name(self):
        return self.name

    def get_description(self):
        return self.description

    def get_content(self):
        return self.content


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


class Border(Sprite):
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
    def __init__(self, player: PlayerSprite, sprite_manager: GameBoard, step=BOX_SIZE):
        self.sprite_manager = sprite_manager
        self.figure = FIRST_FIGURE
        self.is_move = True
        self.prew_ticks = 0
        self.timer = 0

        self.player = player
        self.step = step

    def update_figure(self, figure):
        self.figure = figure

    def handle(self):
        pressed = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        rect = self.player.get_rect()

        if not self.is_move:
            self.timer += pygame.time.get_ticks() - self.prew_ticks
            self.prew_ticks = pygame.time.get_ticks()
            if self.timer > 100:
                self.timer = 0
                self.is_move = True

        if pressed[pygame.K_a]:
            if self.is_move:
                move_x -= self.step
                self.is_move = False
                self.prew_ticks = pygame.time.get_ticks()
        if pressed[pygame.K_d]:
            if self.is_move:
                move_x += self.step
                self.is_move = False
                self.prew_ticks = pygame.time.get_ticks()
        if pressed[pygame.K_s]:
            if self.is_move:
                move_y += self.step
                self.is_move = False
                self.prew_ticks = pygame.time.get_ticks()
        if pressed[pygame.K_w]:
            if self.is_move:
                move_y -= self.step
                self.is_move = False
                self.prew_ticks = pygame.time.get_ticks()

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

        if pressed[pygame.K_f]:
            x, y = pygame.mouse.get_pos()
            box = Figure(self.figure, self.getboxpos(x, y))
            if not self.sprite_manager.collides_solid(box):
                self.sprite_manager.add_solid(box)

    def getboxpos(self, x, y):
        print(self.player.rect.x, self.player.rect.y, x, y)
        x_center = self.player.rect.x + self.player.image.get_width() // 2
        y_center = self.player.rect.y + self.player.image.get_height() // 2
        x, y = x - x_center, -1 * y + y_center
        print(x, y)
        number_col = x_center // BOX_SIZE
        number_row = y_center // BOX_SIZE
        if x > 0 and y > 0:
            if x > y:
                print('right')
                x_box, y_box = number_col * 50 + 50, number_row * 50
                return x_box, y_box
            else:
                print('up')
                x_box, y_box = number_col * 50, number_row * 50 - 50
                return x_box, y_box
        elif x > 0 > y:
            if x > abs(y):
                print('right')
                x_box, y_box = number_col * 50 + 50, number_row * 50
                return x_box, y_box
            else:
                print('down')
                x_box, y_box = number_col * 50, number_row * 50 + 50
                return x_box, y_box
        elif x < 0 < y:
            if abs(x) > y:
                print(5)
                x_box, y_box = number_col * 50 - 50, number_row * 50
                return x_box, y_box
            else:
                print(6, 'up')
                x_box, y_box = number_col * 50, number_row * 50 - 50
                return x_box, y_box
        elif x < 0 and y < 0:
            if x > y:
                print('down')
                x_box, y_box = number_col * 50, number_row * 50 + 50
                return x_box, y_box
            else:
                print(8, 'left')
                x_box, y_box = number_col * 50 - 50, number_row * 50
                return x_box, y_box


def format_timedelta(delta):
    minutes = delta.seconds // 60
    seconds = delta.seconds - minutes * 60
    return f"{minutes:02d}:{seconds:02d}"


class TetrisGame(Page):
    GRASS = pygame.transform.scale(load_image("grass.png"), (WIDTH, HEIGHT))
    FIGURES = {"Г": FOURTH_FIGURE, "|__": FIRST_FIGURE, "L": THIRD_FIGURE, "__|": SECOND_FIGURE}

    def __init__(self, player: PlayerSprite, level, ui_manager: pygame_gui.UIManager):

        self.player = player
        self.ui_manager = ui_manager
        self.start = datetime.datetime.now()

        self.sprite_manager = GameBoard()
        self.sprite_manager.all_sprites.add(player)
        self.sprite_manager.add_solid(Border(1, 1, WIDTH, 1))
        self.sprite_manager.add_solid(Border(1, HEIGHT - 1, WIDTH - 1, HEIGHT - 1))

        self.sprite_manager.add_solid(Border(1, 1, 1, HEIGHT - 1))
        self.sprite_manager.add_solid(Border(WIDTH - 1, 1, WIDTH - 1, HEIGHT - 1))
        self.construct_ui()

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

    def construct_ui(self):

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, HEIGHT - 50), (WIDTH, HEIGHT)),
            starting_layer_height=0,
            manager=self.ui_manager

        )
        self.time = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect((WIDTH - 130, HEIGHT - 50), (WIDTH - 100, HEIGHT - 40)),
            html_text="Время: 00:00",
            layer_starting_height=1,
            manager=self.ui_manager
        )

        self.figures = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect((WIDTH - 200, HEIGHT - 90), (60, 100)),
            item_list=list(TetrisGame.FIGURES.keys()),
            starting_height=1,
            manager=self.ui_manager
        )

    def update(self):
        self.movement_control.handle()
        self.sprite_manager.update()
        current = datetime.datetime.now()

        delta = current - self.start

        self.time.html_text = f"Время: {format_timedelta(delta)}"
        self.time.rebuild()

    def draw(self, screen):
        screen.blit(TetrisGame.GRASS, (0, 0))
        self.sprite_manager.draw(screen)

    def handle_event(self, event):
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            text = event.text
            self.movement_control.update_figure(TetrisGame.FIGURES[text])
