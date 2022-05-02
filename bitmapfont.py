import pygame
from pygame.locals import *

class BitmapFont():
    def __init__(self, font_filename, width, height, colorkey=None):
        '''Load the font spritesheet onto a surface'''
        self._image = pygame.image.load(font_filename)
        if colorkey:
            self._image.set_colorkey(colorkey)
        self._char_width = width
        self._char_height = height
        self._cols = int(self._image.get_rect().width / self._char_width)
        self._rows = int(self._image.get_rect().height / self._char_height)

    @property
    def info(self):
        return f'cols, rows == {(self._cols, self._rows)}\n'\
               f''

    def to_index(self, char):
        '''Given a character, return an index'''
        return ord(char) - ord(' ')

    #def draw_image(self, surface, x, y):
    #    surface.blit(self._image, self._image.rect)

    def index_to_offsets(self, char_index):
        offset_x = (char_index % self._cols) * self._char_width
        offset_y = int(char_index / self._cols) * self._char_height
        return offset_x, offset_y

    def char_to_offsets(self, char):
        char_index = self.to_index(char)
        #print(f'{char}:{char_index} {offset_x=}, {offset_y=}')
        return self.index_to_offsets(char_index)

    def draw(self, surface, message, x, y):
        '''Writes a message onto a surface'''
        x_orig = x
        for char in message:
            if char == '\n':
                y += self._char_height
                x = x_orig
            else:
                offset_x, offset_y = self.char_to_offsets(char)
                src_rect = (offset_x, offset_y, self._char_width, self._char_height)
                surface.blit(self._image, (x, y, self._char_width, self._char_height), src_rect)
                x += self._char_width

    def centre(self, surface, message, y):
        width = len(message) * self._char_width
        halfWidth = surface.get_rect().width
        x = (halfWidth - width) / 2
        self.draw(surface, message, x, y)
