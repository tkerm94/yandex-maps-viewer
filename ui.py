import re

from settings import *


class UI:
    def __init__(self, screen, font, app=None):
        self.app = app
        self.screen = screen
        self.font = font
        self.big_font = pygame.font.Font(pygame.font.get_default_font(), 60)
        self.width = UI_BUTTONS_WIDTH
        self.height = HEIGHT - UI_INPUT_HEIGHT - UI_ADDRESS_HEIGHT - 4 * GAP
        self.active_input = False
        self.input_text = ""
        self.pos = (
            MAP_WIDTH + 2 * GAP,
            UI_INPUT_HEIGHT + 2 * GAP,
        )
        self.buttons = {
            "input": pygame.Rect(0, 0, 0, 0),
            "search": pygame.Rect(0, 0, 0, 0),
            "clear": pygame.Rect(0, 0, 0, 0),
            "mode": pygame.Rect(0, 0, 0, 0),
            "postcode": pygame.Rect(0, 0, 0, 0),
        }
        self.set_ui()

    def set_ui(self):
        btns = list(filter(lambda x: x != "input", self.buttons.keys()))
        button_height = (self.height - GAP * (len(btns) - 1)) / len(btns)
        for i, button in enumerate(btns):
            self.buttons[button].x = self.pos[0]
            self.buttons[button].y = int(self.pos[1] + i * (GAP + button_height))
            self.buttons[button].width = self.width
            self.buttons[button].height = int(button_height)
        if "input" in self.buttons.keys():
            self.buttons["input"].x = GAP
            self.buttons["input"].y = GAP
            self.buttons["input"].width = WIDTH - 2 * GAP
            self.buttons["input"].height = UI_INPUT_HEIGHT

    def render(self, mousepos):
        for text, rect in self.buttons.items():
            if text == "input":
                if self.active_input:
                    pygame.draw.rect(
                        self.screen,
                        UI_INPUT_ACTIVE_COLOR,
                        rect,
                        width=2,
                        border_radius=5,
                    )
                else:
                    pygame.draw.rect(
                        self.screen,
                        UI_INPUT_INACTIVE_COLOR,
                        rect,
                        width=2,
                        border_radius=5,
                    )
                text = self.font.render(self.input_text, True, UI_INPUT_TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
            elif rect.collidepoint(mousepos[0], mousepos[1]):
                pygame.draw.rect(
                    self.screen, UI_BUTTON_HOVER_COLOR, rect, border_radius=5
                )
                text = self.font.render(text, True, UI_TEXT_ACTIVE_COLOR)
                text_rect = text.get_rect(center=rect.center)
            else:
                pygame.draw.rect(self.screen, UI_BG_COLOR, rect, border_radius=5)
                text = self.font.render(text, True, UI_TEXT_INACTIVE_COLOR)
                text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def check_click(self, mousepos):
        self.active_input = False
        for text, rect in self.buttons.items():
            if rect.collidepoint(mousepos[0], mousepos[1]):
                return self.process_button(text)
        return ""

    def process_input(self, event):
        if event.key == pygame.K_RETURN:
            self.active_input = False
        elif event.key == pygame.K_BACKSPACE:
            if self.input_text:
                self.input_text = self.input_text[:-1]
        elif not re.search("[^a-z A-Z а-я А-Я ёЁ 0-9 \-\.\"',]", event.unicode):
            if len(self.input_text) < 65:
                self.input_text += event.unicode

    def process_button(self, text):
        if text == "input":
            self.active_input = True
        else:
            return text
