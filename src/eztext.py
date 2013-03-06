# input lib
from pygame.locals import *
import pygame, string
from config import FONT, FONTSCALE

class ConfigError(KeyError): pass

class Config:
    """ A utility for configuration """
    def __init__(self, options, *look_for):
        assertions = []
        for key in look_for:
            if key[0] in options.keys(): setattr(self, key[0], options[key[0]])
            else: setattr(self, key[0], key[1])
            assertions.append(key[0])
        for key in options.keys():
            if key not in assertions: raise ConfigError(key+' not expected as option')

class Input:
    """ A text input for pygame apps """
    def __init__(self, **options):
        """ Options: x, y, font, color, restricted, maxlength, prompt """
        self.options = Config(options, ['x', 0], ['y', 0], ['font', pygame.font.Font(FONT, int(32*FONTSCALE))],
                              ['color', (0,0,0)], ['restricted', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'],
                              ['maxlength', -1], ['prompt', ''], ['handle_enter', None])
        self.x = self.options.x; self.y = self.options.y
        self.font = self.options.font
        self.color = self.options.color
        self.restricted = self.options.restricted
        self.maxlength = self.options.maxlength
        self.prompt = self.options.prompt; self.value = ''
        self.shifted = False
        self._handle_enter = self.options.handle_enter

    def set_pos(self, x, y):
        """ Set the position to x, y """
        self.x = x
        self.y = y

    def set_font(self, font):
        """ Set the font for the input """
        self.font = font

    def draw(self, surface):
        """ Draw the text input to a surface """
        text = self.font.render(self.prompt+self.value, 1, self.color)
        surface.blit(text, (self.x, self.y))

    def handle_enter(self):
        if self._handle_enter:
            self._handle_enter()

    def update(self, events):
        """ Update the input based on passed events """
        for event in events:
            if event.type == KEYUP:
                if event.key == K_LSHIFT or event.key == K_RSHIFT: self.shifted = False
            if event.type == KEYDOWN:
                if event.key == K_BACKSPACE: self.value = self.value[:-1]
                elif event.key == K_LSHIFT or event.key == K_RSHIFT: self.shifted = True
                elif event.key == K_SPACE: self.value += ' '
                elif event.key == K_RETURN: self.handle_enter()
                value = {
                    K_a: ('a', 'A'),
                    K_b: ('b', 'B'),
                    K_c: ('c', 'C'),
                    K_d: ('d', 'D'),
                    K_e: ('e', 'E'),
                    K_f: ('f', 'F'),
                    K_g: ('g', 'G'),
                    K_h: ('h', 'H'),
                    K_i: ('i', 'I'),
                    K_j: ('j', 'J'),
                    K_k: ('k', 'K'),
                    K_l: ('l', 'L'),
                    K_m: ('m', 'M'),
                    K_n: ('n', 'N'),
                    K_o: ('o', 'O'),
                    K_p: ('p', 'P'),
                    K_q: ('q', 'Q'),
                    K_r: ('r', 'R'),
                    K_s: ('s', 'S'),
                    K_t: ('t', 'T'),
                    K_u: ('u', 'U'),
                    K_v: ('v', 'V'),
                    K_w: ('w', 'W'),
                    K_x: ('x', 'X'),
                    K_y: ('y', 'Y'),
                    K_z: ('z', 'Z'),
                    K_0: ('0', ')'),
                    K_1: ('1', '!'),
                    K_2: ('2', '@'),
                    K_3: ('3', '#'),
                    K_4: ('4', '$'),
                    K_5: ('5', '%'),
                    K_6: ('6', '^'),
                    K_7: ('7', '&'),
                    K_8: ('8', '*'),
                    K_9: ('9', '('),
                    K_BACKQUOTE: ('`', '~'),
                    K_MINUS: ('-', '_'),
                    K_EQUALS: ('=', '+'),
                    K_LEFTBRACKET: ('[', '{'),
                    K_RIGHTBRACKET: (']', '}'),
                    K_BACKSLASH: ('\\', '|'),
                    K_SEMICOLON: (';', ':'),
                    K_QUOTE: ('\'', '"'),
                    K_COMMA: (',', '<'),
                    K_PERIOD: ('.', '>'),
                    K_SLASH: ('/', '?'),
                }.get(event.key, ('', ''))[self.shifted]
                if value in self.restricted: self.value += value
        if len(self.value) > self.maxlength and self.maxlength >= 0: self.value = self.value[:-1]
