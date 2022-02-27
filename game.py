import datetime

import pygame
import pygame_gui
from pygame.sprite import AbstractGroup, Sprite

from database import ScoreDatabase, Score
from event import Signal
from page import Page
from util import load_image, HEIGHT, WIDTH, BOX_SIZE

PANEL_HEIGHT = 50

FIRST_FIGURE = ["B  ",
                "BBB"]
SECOND_FIGURE = ["  B",
                 "BBB"]
THIRD_FIGURE = ["B ",
                "B ",
                "BB"]
FOURTH_FIGURE = ["BB",
                 "B ",
                 "B "]
FIFTH_FIGURE = ["B"]


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

    def __init__(self, player: PlayerSprite):
        self.player = player
        self.all_sprites = pygame.sprite.Group()
        self.solid_sprites = pygame.sprite.Group()
        self.solid_and_boxes = pygame.sprite.Group()
        self.boxes = pygame.sprite.Group()

    def add_solid(self, sprite):
        self.all_sprites.add(sprite)
        self.solid_and_boxes.add(sprite)
        self.solid_sprites.add(sprite)

    def add_box(self, box):
        self.all_sprites.add(box)
        self.solid_and_boxes.add(box)
        self.boxes.add(box)

    def collides_box(self, sprite):
        if self.collides_solid(sprite):
            return True
        for box in self.boxes:
            if pygame.sprite.collide_mask(sprite, box):
                return True
        return False

    def update(self, *args, **kwargs):
        self.all_sprites.update(*args, **kwargs)

    def draw(self, screen):
        self.all_sprites.draw(screen)
        screen.blit(self.player.image, self.player.rect)

    def collides_solid(self, sprite):
        for solid in self.solid_sprites:
            if pygame.sprite.collide_mask(sprite, solid):
                return True
        return False


class MovementController:
    def __init__(self, player: PlayerSprite, sprite_manager: GameBoard, step=BOX_SIZE):
        self.win = Signal()

        self.board_rect = pygame.Rect((0, 0), (WIDTH, HEIGHT - PANEL_HEIGHT))
        self.sprite_manager = sprite_manager
        self.figure = FIRST_FIGURE
        self.is_move = True
        self.figures_count = 0
        self.prew_ticks = 0
        self.timer = 0

        self.player = player
        self.step = step

    def update_figure(self, figure):
        self.figure = figure

    def check_win(self):
        print(self.board_rect.width, self.board_rect.h)
        for x in range(self.board_rect.width // BOX_SIZE):
            for y in range(self.board_rect.height // BOX_SIZE):
                collides = False
                for sprite in self.sprite_manager.solid_and_boxes:
                    if sprite.rect.collidepoint(x * BOX_SIZE, y * BOX_SIZE):
                        collides = True
                        break
                if not collides:
                    return
        print("thats a win baby!!!")
        self.win.emit()

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
        if self.sprite_manager.collides_solid(self.player) or not self.board_rect.colliderect(new_rect):
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

        if pygame.mouse.get_pressed(3)[2]:
            x, y = pygame.mouse.get_pos()
            pos = self.getboxpos(x, y)
            if pos is None:
                return
            box = Figure(self.figure, pos)
            if not self.sprite_manager.collides_box(box) and box.rect.colliderect(self.board_rect):
                self.sprite_manager.add_box(box)
                self.figures_count += 1
                self.check_win()

    def getboxpos(self, x, y):
        x_center = self.player.rect.x + self.player.image.get_width() // 2
        y_center = self.player.rect.y + self.player.image.get_height() // 2
        x, y = x - x_center, -1 * y + y_center
        number_col = x_center // BOX_SIZE
        number_row = y_center // BOX_SIZE
        if x > 0 and y > 0:
            if x > y:
                x_box, y_box = number_col * BOX_SIZE + BOX_SIZE, number_row * BOX_SIZE
                return x_box, y_box
            else:
                x_box, y_box = number_col * BOX_SIZE, number_row * BOX_SIZE - BOX_SIZE
                return x_box, y_box
        elif x > 0 > y:
            if x > abs(y):
                x_box, y_box = number_col * BOX_SIZE + BOX_SIZE, number_row * BOX_SIZE
                return x_box, y_box
            else:
                x_box, y_box = number_col * BOX_SIZE, number_row * BOX_SIZE + BOX_SIZE
                return x_box, y_box
        elif x < 0 < y:
            if abs(x) > y:
                x_box, y_box = number_col * BOX_SIZE - BOX_SIZE, number_row * BOX_SIZE
                return x_box, y_box
            else:
                x_box, y_box = number_col * BOX_SIZE, number_row * BOX_SIZE - BOX_SIZE
                return x_box, y_box
        elif x < 0 and y < 0:
            if x > y:
                x_box, y_box = number_col * BOX_SIZE, number_row * BOX_SIZE + BOX_SIZE
                return x_box, y_box
            else:
                x_box, y_box = number_col * BOX_SIZE - BOX_SIZE, number_row * BOX_SIZE
                return x_box, y_box


def format_timedelta(delta):
    minutes = delta.seconds // 60
    seconds = delta.seconds - minutes * 60
    return f"{minutes:02d}:{seconds:02d}"


class TetrisGame(Page):
    GRASS = pygame.transform.scale(load_image("grass.png"), (WIDTH, HEIGHT))
    FIGURES = {"Г": FOURTH_FIGURE, "|__": FIRST_FIGURE, "L": THIRD_FIGURE, "__|": SECOND_FIGURE, "*": FIFTH_FIGURE}

    def __init__(self, player: PlayerSprite, level: Level, ui_manager: pygame_gui.UIManager, database: ScoreDatabase):

        self.game_win = Signal()
        self.game_exit = Signal()

        self.database = database
        self.player = player
        self.ui_manager = ui_manager
        self.level = level
        self.start = datetime.datetime.now()

        self.sprite_manager = GameBoard(player)
        self.sprite_manager.all_sprites.add(player)
        '''   self.sprite_manager.add_solid(Border(1, 1, WIDTH, 1))
        self.sprite_manager.add_solid(Border(1, HEIGHT - 1, WIDTH - 1, HEIGHT - 1))

        self.sprite_manager.add_solid(Border(1, 1, 1, HEIGHT - 1))
        self.sprite_manager.add_solid(Border(WIDTH - 1, 1, WIDTH - 1, HEIGHT - 1))
        '''
        self.construct_ui()
        content = level.content
        for i in range(len(content)):
            s = content[i]
            y = i * BOX_SIZE
            for j in range(len(s)):
                c = s[j]
                x = j * BOX_SIZE
                if c == 'X':
                    self.sprite_manager.add_solid(BrickSprite((x, y)))
                elif c == 'P':
                    self.player.rect.x, self.player.rect.y = x, y
        self.movement_control = MovementController(
            player, self.sprite_manager
        )
        self.movement_control.win.connect(self.win)

    def construct_ui(self):

        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect((0, HEIGHT - PANEL_HEIGHT), (WIDTH, HEIGHT)),
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

    def win(self):

        date = datetime.datetime.now()
        level = self.level.name
        delta = datetime.datetime.now() - self.start
        figures_placed = self.movement_control.figures_count

        score = Score(date, level, delta.seconds, figures_placed)
        self.database.save(score)
        self.game_win.emit()

        size_x = 300
        size_y = 200
        half_size_x = size_x // 2
        half_size_y = size_y // 2

        pygame_gui.windows.UIMessageWindow(
            rect=pygame.Rect(WIDTH // 2 - half_size_x, HEIGHT // 2 - half_size_y, size_x, size_y),
            window_title="Победа!",
            html_message=f"Поздравляем! Вы победили!"
                         f"<br>Блоков установлено: {figures_placed}"
                         f"<br>Времени потрачено: {format_timedelta(delta)}",
            manager=self.ui_manager
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            text = event.text
            self.movement_control.update_figure(TetrisGame.FIGURES[text])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                size_x = 300
                size_y = 200
                half_size_x = size_x // 2
                half_size_y = size_y // 2

                pygame_gui.windows.UIConfirmationDialog(
                    rect=pygame.Rect(WIDTH // 2 - half_size_x, HEIGHT // 2 - half_size_y, size_x, size_y),
                    window_title="Уверены?",
                    action_long_desc="Вы уверены, что хотите выйти?",
                    manager=self.ui_manager
                )
        elif event.type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED:
            self.game_exit.emit()
