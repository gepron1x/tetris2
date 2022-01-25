# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import sys

import pygame
import pygame_gui

from event import Signal
from game import PlayerSprite, TetrisGame, Level

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


class MainPage(Page):
    BACKGROUND = pygame.Surface((WIDTH, HEIGHT))
    LEVELS, STATISTICS = 0, 1

    def __init__(self, ui_manager):
        self.levels = Signal()
        self.statistics = Signal()

        self.levels_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((WIDTH // 2 - 100, 250), (200, 50)),
                                                          text='Выбор уровня',
                                                          manager=ui_manager)

        self.statistics_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((WIDTH // 2 - 100, 310), (200, 50)),
            text='Статистика',
            manager=ui_manager)

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self.click(event.ui_element)

    def draw(self, screen):
        screen.blit(MainPage.BACKGROUND, (0, 0))

    def click(self, element):
        print("yes")
        if element == self.statistics_button:
            self.statistics.emit()
        elif element == self.levels_button:
            print("yes")
            self.levels.emit()


class Levels(Page):

    def __init__(self, ui_manager: pygame_gui.UIManager, levels):
        self.level_chosen = Signal()
        self.button_to_level = dict()
        panel_width = 300
        panel_height = 50

        x = panel_width // 2

        for index, level in enumerate(levels):
            y = 200 + (panel_height + 20) * index
            panel = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect(
                    (x, y), (panel_width, panel_height)
                ),
                starting_layer_height=0,
                manager=ui_manager
            )
            text = pygame_gui.elements.UITextBox(
                relative_rect=pygame.Rect((x + 5, y + 1), (200, 49)),
                html_text=f"{level.get_name()}: {level.get_description()}",
                manager=ui_manager
            )
            button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((x + 210, y), (80, 49)),
                text="Играть",
                manager=ui_manager
            )
            self.button_to_level[button] = level

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            element = event.ui_element
            level = self.button_to_level[element]
            self.level_chosen.emit(level)

    def draw(self, screen):
        screen.blit(MainPage.BACKGROUND, (0, 0))


class TetrisGameMain:

    def __init__(self, player: PlayerSprite, ui_manager: pygame_gui.UIManager, levels):
        self.player = player
        self.ui_manager = ui_manager
        self.page = MainPage(ui_manager)
        self.page.levels.connect(self.set_levels_page)
        self.levels = levels

    def set_levels_page(self):
        self.ui_manager.clear_and_reset()
        self.page = Levels(self.ui_manager, self.levels)
        self.page.level_chosen.connect(self.set_game_page)

    def set_game_page(self, level):
        self.ui_manager.clear_and_reset()
        self.page = TetrisGame(self.player, level.get_content(), self.ui_manager)


def main():
    running = True
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    manager = pygame_gui.UIManager((WIDTH, HEIGHT))
    pygame.display.set_icon(PlayerSprite.IMAGE)
    pygame.display.set_caption('Tetris 2 - Строй коммунизм не выходя из дома!')

    clock = pygame.time.Clock()
    player = PlayerSprite("player")
    game = TetrisGameMain(player, manager, [Level("Уровень 1", "", ["            ",
                                                                    "            ",
                                                                    "B        BBB",
                                                                    "BB  B      B",
                                                                    "BB        BB",
                                                                    "B  B      BB",
                                                                    "B  B  B BB  "])])
    # page = Levels(manager, [Level("Уровень 1", "", []), Level("Уровень 2", "", []), Level("Уровень 3", "", [])])
    # page = MainPage(manager)
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.page.handle_event(event)
            game.ui_manager.process_events(event)
        game.ui_manager.update(time_delta)
        game.page.update()
        game.page.draw(screen)
        game.ui_manager.draw_ui(screen)
        pygame.display.flip()
        clock.tick(30)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
