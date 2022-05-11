import pygame
from tools import Pencil, Line, Rect, Circle, Type
import config
from bitmapfont import BitmapFont

''' App: contains several Scenes
    Scene: describes a particular stage of an App, does not necessarily display anything
    e.g. splash screen, menu screen, level
    InputContext: applies to a particular scene
    Layer: visual part that is displayed
'''

SCREEN_WIDTH = config.SCREEN_WIDTH
SCREEN_HEIGHT = config.SCREEN_HEIGHT

BOTTOM_BAR_Y_POS = config.SCREEN_HEIGHT - config.FONT_HEIGHT
CURSOR_COORDS_STR_LEN = len(f'{SCREEN_WIDTH},{SCREEN_HEIGHT}')
CURSOR_COORDS_X_POS = config.SCREEN_WIDTH - config.FONT_WIDTH * CURSOR_COORDS_STR_LEN

class Palette:
    def __init__(self):
        self.colours = [config.BLACK, config.WHITE, config.BLUE, config.ORANGE]
        self.palette = pygame.Surface((len(self.colours), 1))
        self.display = pygame.Surface((len(self.colours) * config.FONT_WIDTH, config.FONT_HEIGHT))
        self.index = 0
        self.init_palette()
        self.refresh_surface()

    @property
    def current_colour(self):
        return self.colours[self.index]

    def init_palette(self):
        for i, colour in enumerate(self.colours):
            pygame.draw.line(self.palette, colour, (i, 0), (i, 0), 1)

    def refresh_surface(self):
        pygame.transform.scale(self.palette, (len(self.colours) * config.FONT_WIDTH, config.FONT_HEIGHT), \
                               dest_surface=self.display)

    def next(self):
        self.index += 1
        self.index %= len(self.colours)

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
        self.palette = Palette()

        self.screen = self.display.screen
        self.clock = self.display.clock
        self.is_running = False
        self.mouse_drag = False
        self.ctrl_down = False
        self.shift_down = False
        self.fill_mode = False
        self.line_thickness = 1
        self.prev_thickness = 1
        self.font = BitmapFont(config.FONT_FILENAME, config.FONT_WIDTH, config.FONT_HEIGHT)

        pygame.key.set_repeat(config.KEY_HOLD_DELAY_MILLISECONDS, config.KEY_HOLD_INTERVAL_MILLISECONDS)
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_rel = pygame.mouse.get_rel()
        self.bg_colour = config.BG_COLOUR
        self.fg_colour = config.FG_COLOUR

        self.init_tools()
        self.clear_canvas()

    def init_tools(self):
        self.tools = {
            'pencil': Pencil(self),
            'line': Line(self),
            'rect': Rect(self),
            'circle': Circle(self),
            'type': Type(self),
        }
        self.tool = self.tools['pencil']
        self.prev_tool = self.tools['pencil']

    def reset_keys_mouse_state(self):
        self.ctrl_down = False
        self.shift_down = False

    def run(self):
        self.is_running = True
        while self.is_running:
            self.update()

    def toggle_fill_mode(self):
        self.fill_mode = not self.fill_mode
        if self.fill_mode:
            self.prev_thickness = self.line_thickness
            self.line_thickness = 0
        else:
            self.line_thickness = self.prev_thickness

    def handle_quit(self):
        self.is_running = False

    def handle_ctrl_down(self, event):
        self.ctrl_down = True
        if event.key == pygame.K_q:
            self.handle_quit()
        if event.key == pygame.K_f:
            self.toggle_fill_mode()
        if event.key == pygame.K_e:
            self.clear_canvas()
        if event.key == pygame.K_BACKQUOTE:
            self.palette.next()
            self.fg_colour = self.palette.current_colour

    def handle_shift_down(self, event):
        self.shift_down = True
        tool_name = None
        if event.key == pygame.K_d:
            tool_name = 'pencil'
        elif event.key == pygame.K_l:
            tool_name = 'line'
        elif event.key == pygame.K_r:
            tool_name = 'rect'
        elif event.key == pygame.K_c:
            tool_name = 'circle'
        elif event.key == pygame.K_t:
            tool_name = 'type'
        if tool_name:
            self.tools[tool_name].activate()

    def handle_mouse_button_down(self):
        self.mouse_drag = True

    def handle_mouse_button_up(self):
        self.tool.button_up()
        self.mouse_drag = False

    def clear_canvas(self):
        self.canvas.fill(self.bg_colour)

    def draw_overlay(self):
        self.tool.draw_cursor()
        # display mouse co-ordinates
        self.font.draw(self.screen, f'{self.mouse_pos[0]:03d},{self.mouse_pos[1]:03d}', CURSOR_COORDS_X_POS, BOTTOM_BAR_Y_POS)
        self.screen.blit(self.palette.display, (0, BOTTOM_BAR_Y_POS))

        if self.ctrl_down:
            self.font.draw(self.screen, 'Q-Quit', 0, BOTTOM_BAR_Y_POS)
        elif self.shift_down:
            self.font.draw(self.screen, 'D-Draw    L-Line   C-Circle    T-Text   E-Erase', 0, BOTTOM_BAR_Y_POS)

    def update_gfx(self):
        # copy canvas to screen buffer
        self.screen.blit(self.canvas, (0,0))
        self.draw_overlay()
        pygame.display.flip()
        self.clock.tick(config.REFRESH_RATE_HZ)

    def get_events(self):
        'Handles user interactivity e.g. keyboard and mouse input'
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

    def process_events(self):
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_rel = pygame.mouse.get_rel()
        if self.mouse_drag:
            self.tool.button_down()

    def update(self):
        self.reset_keys_mouse_state()
        self.get_events()
        self.process_events()
        self.update_gfx()

def main():
    a = App()
    a.run()

if __name__ == '__main__':
    main()
