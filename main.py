import pygame
from bitmapfont import BitmapFont

''' App: contains several Scenes
    Scene: describes a particular stage of an App, does not necessarily display anything
    e.g. splash screen, menu screen, level
    InputContext: applies to a particular scene
    Layer: visual part that is displayed
'''


SCREEN_WIDTH=600
SCREEN_HEIGHT=400
FRAMES_PER_SECOND=60
colour_screen=(0,64,128)
colour_circle=(127,0,0)
colour_line=(64*3,64*3,64*3)
FONT_FILENAME = 'font-7x9.png'
FONT_HEIGHT = 9
FONT_WIDTH = 7
BOTTOM_BAR_Y_POS = SCREEN_HEIGHT - FONT_HEIGHT
KEY_HOLD_DELAY_MILLISECONDS = 200
KEY_HOLD_INTERVAL_MILLISECONDS = 100

class Tool:
    def __init__(self, app):
        self.screen = app.screen
        self.canvas = app.canvas
        self.app = app

    @property
    def mouse_pos(self):
        return self.app.mouse_pos

    def activate(self):
        self.app.tool_prev = self.app.tool
        self.app.tool = self

    def draw_cursor(self):
        pygame.draw.circle(self.screen, colour_line, self.mouse_pos, 1)

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
        pygame.draw.circle(self.canvas, colour_circle, self.mouse_pos, 1)

class Line(Tool):
    ''' init state, no points, just draw dot
        down click: p1, draw line
        down click: p2, canvas line
    '''
    name = 'Line'
    def __init__(self, app):
        super().__init__(app)
        self.start_pos = None
        self.end_pos = None

    def activate(self):
        super().activate()
        self.start_pos = None
        self.end_pos = None

    def cancel(self):
        self.start_pos = None

    def handle_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.cancel()

    def draw_cursor(self):
        if self.start_pos:
            pygame.draw.aaline(self.screen, colour_line, self.start_pos, self.mouse_pos, 1)
        else:
            pygame.draw.circle(self.screen, colour_line, self.mouse_pos, 1)

    def button_down(self):
        if not self.start_pos:
            self.start_pos = self.mouse_pos

    def button_up(self):
        if self.start_pos:
            self.apply()

    def apply(self):
        pygame.draw.aaline(self.canvas, colour_line, self.start_pos, self.mouse_pos, 1)
        self.start_pos = self.mouse_pos

    def exit(self):
        self.start_pos = None
        self.end_pos = None
        super().exit()

class Type(Tool):
    name = 'Type'
    def __init__(self, app):
        super().__init__(app)
        self.text = ''
        self.font = BitmapFont(FONT_FILENAME, 7, 9)

    def handle_event(self, event):
        if event.key == pygame.K_ESCAPE:
            self.text = ''
            self.exit()
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self.text += '\n'
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            self.text += event.unicode

    def draw_cursor(self):
        self.font.draw(self.screen, self.text, *self.mouse_pos)

    def button_down(self):
        self.apply()

    def apply(self):
        self.font.draw(self.canvas, self.text, *self.mouse_pos)

class InputContext:
    def __init__(self):
        pass


class Display:
    def __init__(self, width, height):
        self.screen = pygame.display.set_mode((width, height), pygame.SCALED)
        self.clock = pygame.time.Clock()
        pygame.mouse.set_visible(False)

class App:
    def __init__(self):
        'Set the name of the EventHandler e.g. menu, character select, bonus'
        self.display = Display(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = self.display.screen
        self.clock = self.display.clock
        self.is_running = False
        self.mouse_down = False
        self.ctrl_down = False
        self.shift_down = False
        self.font = BitmapFont(FONT_FILENAME, 7, 9)
        pygame.key.set_repeat(KEY_HOLD_DELAY_MILLISECONDS, KEY_HOLD_INTERVAL_MILLISECONDS)
        self.mouse_pos = pygame.mouse.get_pos()
        self.init_tools()

    def init_tools(self):
        self.tools = {'pencil': Pencil(self), 'type': Type(self), 'line': Line(self)}
        self.tool = self.tools['pencil']
        self.prev_tool = self.tools['pencil']

    def reset_keys_mouse_state(self):
        self.ctrl_down = False
        self.shift_down = False
        self.mouse_button_down = False

    def run(self):
        self.is_running = True
        while self.is_running:
            self.update()

    def handle_quit(self):
        self.is_running = False

    def handle_ctrl_down(self, event):
        self.ctrl_down = True
        if event.key == pygame.K_q:
            self.handle_quit()

    def handle_shift_down(self, event):
        self.shift_down = True
        if event.key == pygame.K_e:
            self.clear_canvas()
        else:
            if event.key == pygame.K_d:
                self.tools['pencil'].activate()
            elif event.key == pygame.K_l:
                self.tools['line'].activate()
            elif event.key == pygame.K_t:
                self.tools['type'].activate()

    def handle_mouse_button_down(self):
        self.mouse_button_down = True
        self.tool.button_down()

    def handle_mouse_button_up(self):
        self.mouse_button_down = False
        self.tool.button_up()

    def clear_canvas(self):
        self.canvas.fill(colour_screen)

    def draw_overlay(self):
        self.tool.draw_cursor()
        # show mouse co-ordinates
        self.font.draw(self.screen, f'{self.mouse_pos[0]:03d},{self.mouse_pos[1]:03d}', 0, 0)

        if self.ctrl_down:
            self.font.draw(self.screen, 'CTRL  Q-Quit', 0, BOTTOM_BAR_Y_POS)

        if self.shift_down:
            self.font.draw(self.screen, 'SHIFT D-Draw    L-Line   T-Text   E-Erase', 0, BOTTOM_BAR_Y_POS)

    def update_mouse_pos(self):
        self.mouse_pos = pygame.mouse.get_pos()

    def update_gfx(self):
        # copy canvas to screen buffer
        self.screen.blit(self.canvas, (0,0))
        self.draw_overlay()
        pygame.display.flip()
        self.clock.tick(FRAMES_PER_SECOND)

    def get_events(self):
        '''Handles user interactivity e.g. keyboard and mouse input'''
        self.update_mouse_pos()
        for event in pygame.event.get():
            # App handles below
            if event.type == pygame.QUIT:
                self.handle_quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_button_down()
            if event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_button_up()
            if event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_SHIFT:
                    self.handle_shift_down(event)
                if event.mod & pygame.KMOD_CTRL:
                    self.handle_ctrl_down(event)
                else:
                    self.tool.handle_event(event)

    def update(self):
        self.reset_keys_mouse_state()
        self.get_events()
        self.update_gfx()

def main():
    a = App()
    a.run()

if __name__ == '__main__':
    main()
