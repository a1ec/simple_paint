import pygame
from pygame.locals import *

class BitmapFont():
    def __init__(self, font_filename, width, height, colorkey=None):
        'Load the font spritesheet onto a surface'
        self.font_map = pygame.image.load(font_filename)
        if colorkey:
            self.font_map.set_colorkey(colorkey)
        self._char_width = width
        self._char_height = height
        self._cols = int(self.font_map.get_rect().width / self._char_width)
        self._rows = int(self.font_map.get_rect().height / self._char_height)

    def to_index(self, char):
        'Given a character, return an index'
        return ord(char) - ord(' ')

    def index_to_offsets(self, char_index):
        offset_x = (char_index % self._cols) * self._char_width
        offset_y = int(char_index / self._cols) * self._char_height
        return offset_x, offset_y

    def char_to_offsets(self, char):
        char_index = self.to_index(char)
        return self.index_to_offsets(char_index)

    def char_to_src_rect(self, char):
        offset_x, offset_y = self.char_to_offsets(char)
        return (offset_x, offset_y, self._char_width, self._char_height)

    def draw_char(self, char, surface, x, y):
        src_rect = self.char_to_src_rect(char)
        dest_rect = (x, y, self._char_width, self._char_height)
        surface.blit(self.font_map, dest_rect, src_rect)

    def draw_text(self, text, surface, x, y):
        'Writes text onto a surface'
        x_orig = x
        for char in text:
            if char == '\n':
                y += self._char_height
                x = x_orig
            else:
                # blit the individual char
                self.draw_char(char, surface, x, y)
                x += self._char_width

    def centre(self, text, surface, y):
        width = len(text) * self._char_width
        half_width = surface.get_rect().width
        x = (half_width - width) * .5
        self.draw_text(surface, text, x, y)
