import pygame
from bitmapfont import BitmapFont
import config

class Tool:
    'Parent class of all tools'
    def __init__(self, app):
        self.screen = app.screen
        self.canvas = app.canvas
        self.app = app

    @property
    def mouse_pos(self):
        return self.app.mouse_pos

    @property
    def mouse_rel(self):
        return self.app.mouse_rel

    def activate(self):
        self.app.tool_prev = self.app.tool
        self.app.tool = self

    def draw_dot(self):
        pygame.draw.line(self.screen, self.app.fg_colour, self.mouse_pos, self.mouse_pos, 1)

    def draw_cursor(self):
        self.draw_dot()

    def draw_cursor_applied(self):
        pass

    def handle_event(self, event):
        pass

    def button_down(self):
        pass

    def button_up(self):
        pass

    def cancel(self):
        pass

    def apply(self):
        pass

    def exit(self):
        self.app.tool = self.app.prev_tool

class Pencil(Tool):
    name = 'Pencil'
    def button_down(self):
        self.apply()

    def apply(self):
        pygame.draw.line(self.canvas, self.app.fg_colour, self.mouse_pos, self.mouse_pos, 1)

class Line(Tool):
    ''' init state, no points, just draw dot
        down click: p1, draw line
        down click: p2, canvas line
    '''
    name = 'Line'
    def __init__(self, app):
        super().__init__(app)
        self.start_pos = None

    def activate(self):
        super().activate()
        self.reset_pos()

    def reset_pos(self):
        self.start_pos = None

    def cancel(self):
        self.start_pos = None

    def handle_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.cancel()

    def draw_cursor_applied(self):
        pygame.draw.line(self.screen, self.app.fg_colour, self.start_pos, self.mouse_pos, 1)

    def draw_cursor(self):
        if self.start_pos:
            self.draw_cursor_applied()
        else:
            self.draw_dot()

    def button_down(self):
        if not self.start_pos:
            self.start_pos = self.mouse_pos

    def button_up(self):
        if self.start_pos and self.start_pos != self.mouse_pos:
            self.apply()

    def apply(self):
        pygame.draw.line(self.canvas, self.app.fg_colour, self.start_pos, self.mouse_pos, 1)
        self.reset_pos()

    def exit(self):
        self.reset_pos()
        super().exit()

class Rect(Line):
    name = 'Rect'

    def __init__(self, app):
        super().__init__(app)
        self.width = 0
        self.height = 0

    def draw_cursor_applied(self):
        if self.start_pos:
            self.left = self.start_pos[0]
            self.top = self.start_pos[1]

            # start_pos should be swapped with mouse_pos if the rect is drawn to the left
            self.width = self.mouse_pos[0] - self.left
            if self.width < 0:
                self.width = -self.width
                self.left = self.mouse_pos[0]

            self.height = self.mouse_pos[1] - self.top
            if self.height < 0:
                self.height = -self.height
                self.top = self.mouse_pos[1]
            pygame.draw.rect(self.screen, self.app.fg_colour, (self.left, self.top, self.width, self.height), self.app.line_thickness)

    def apply(self):
        pygame.draw.rect(self.canvas, self.app.fg_colour, (self.left, self.top, self.width, self.height), self.app.line_thickness)
        self.reset_pos()

class Circle(Line):
    name = 'Circle'
    def get_radius(self):
        self.a = complex(*self.start_pos)
        self.b = complex(*self.mouse_pos)
        return abs(self.b - self.a)

    def draw_cursor_applied(self):
        if self.start_pos:
            pygame.draw.circle(self.screen, self.app.fg_colour, self.start_pos, self.get_radius(), self.app.line_thickness)

    def apply(self):
        pygame.draw.circle(self.canvas, self.app.fg_colour, self.start_pos, self.get_radius(), self.app.line_thickness)
        self.reset_pos()

class Type(Tool):
    name = 'Type'
    def __init__(self, app):
        super().__init__(app)
        # any black in the original font will be transparent
        self.font = BitmapFont(config.FONT_FILENAME, config.FONT_WIDTH, config.FONT_HEIGHT, colorkey=config.BLACK)
        self.init_text()

    def init_text(self):
        self.rows = 1
        self.text = ''
        self.dropped_first_char = False

    def handle_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.text = ''
            self.exit()
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.text += '\n'
            self.rows += 1
        elif event.key == pygame.K_BACKSPACE:
            if len(self.text) > 0:
                if self.text[-1] == '\n':
                    self.rows -= 1
                self.text = self.text[:-1]
        else:
            if self.dropped_first_char:
                self.text += event.unicode
            else:
                self.dropped_first_char = True

    @property
    def len_last_row(self):
        return len(self.text.split('\n')[-1])

    def draw_text_cursor_pos(self):
        left = self.mouse_pos[0] + self.len_last_row * config.FONT_WIDTH
        top = self.mouse_pos[1] + (self.rows - 1) * config.FONT_HEIGHT
        pygame.draw.rect(self.screen, self.app.fg_colour, (left, top, config.FONT_WIDTH, config.FONT_HEIGHT), 0)

    def draw_cursor(self):
        self.font.draw_text(self.text, self.screen, *self.mouse_pos)
        self.draw_text_cursor_pos()

    def button_down(self):
        self.apply()

    def apply(self):
        self.font.draw_text(self.text, self.canvas, *self.mouse_pos)

    def exit(self):
        self.init_text()
        super().exit()
