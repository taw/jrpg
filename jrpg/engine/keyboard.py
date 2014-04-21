
import pygame

NAMEKEYBOARD = {
    pygame.K_BACKSPACE: 'Backspace',
    pygame.K_BREAK: 'Break',
    pygame.K_CAPSLOCK: 'Capslock',
    pygame.K_CLEAR: 'Clear',
    pygame.K_DELETE: 'Del',
    pygame.K_DOWN: 'Down',
    pygame.K_END: 'End',
    pygame.K_ESCAPE: 'Escape',
    pygame.K_EURO: 'Euro',
    pygame.K_F1: 'F1',
    pygame.K_F2: 'F2',
    pygame.K_F3: 'F3',
    pygame.K_F4: 'F4',
    pygame.K_F5: 'F5',
    pygame.K_F6: 'F6',
    pygame.K_F7: 'F7',
    pygame.K_F8: 'F8',
    pygame.K_F9: 'F9',
    pygame.K_F10: 'F10',
    pygame.K_F11: 'F11',
    pygame.K_F12: 'F12',
    pygame.K_F13: 'F13',
    pygame.K_F14: 'F14',
    pygame.K_F15: 'F15',
    pygame.K_FIRST: 'First',
    pygame.K_HELP: 'Help',
    pygame.K_HOME: 'Home',
    pygame.K_INSERT: 'Ins',
    pygame.K_LALT: 'L.Alt',
    pygame.K_LAST: 'Last',
    pygame.K_LCTRL: 'L.Ctrl',
    pygame.K_LEFT: 'Left',
    pygame.K_LMETA: 'L.Meta',
    pygame.K_LSHIFT: 'L.Shift',
    pygame.K_LSUPER: 'L.Super',
    pygame.K_MENU: 'Menu',
    pygame.K_MODE: 'Mode',
    pygame.K_NUMLOCK: 'Numlock',
    pygame.K_PAGEDOWN: 'PgDn',
    pygame.K_PAGEUP: 'PgUp',
    pygame.K_PAUSE: 'Pause',
    pygame.K_POWER: 'Power',
    pygame.K_PRINT: 'Print',
    pygame.K_RALT: 'R.Alt',
    pygame.K_RCTRL: 'R.Ctrl',
    pygame.K_RETURN: 'Return',
    pygame.K_RIGHT: 'Right',
    pygame.K_RMETA: 'R.Meta',
    pygame.K_RSHIFT: 'R.Shift',
    pygame.K_RSUPER: 'R.Super',
    pygame.K_SCROLLOCK: 'Scrolllock',
    pygame.K_SYSREQ: 'SysRq',
    pygame.K_TAB: 'Tab',
    pygame.K_UP: 'Up',
    pygame.K_SPACE: 'Space',
    pygame.K_a: 'a',
    pygame.K_b: 'b',
    pygame.K_c: 'c',
    pygame.K_d: 'd',
    pygame.K_e: 'e',
    pygame.K_f: 'f',
    pygame.K_g: 'g',
    pygame.K_h: 'h',
    pygame.K_i: 'i',
    pygame.K_j: 'j',
    pygame.K_k: 'k',
    pygame.K_l: 'l',
    pygame.K_m: 'm',
    pygame.K_n: 'n',
    pygame.K_o: 'o',
    pygame.K_p: 'p',
    pygame.K_q: 'q',
    pygame.K_r: 'r',
    pygame.K_s: 's',
    pygame.K_t: 't',
    pygame.K_u: 'u',
    pygame.K_v: 'v',
    pygame.K_w: 'w',
    pygame.K_x: 'x',
    pygame.K_y: 'y',
    pygame.K_z: 'z',
    pygame.K_0: '0',
    pygame.K_1: '1',
    pygame.K_2: '2',
    pygame.K_3: '3',
    pygame.K_4: '4',
    pygame.K_5: '5',
    pygame.K_6: '6',
    pygame.K_7: '7',
    pygame.K_8: '8',
    pygame.K_9: '9',
    pygame.K_KP0: 'keypad-0',
    pygame.K_KP1: 'keypad-1',
    pygame.K_KP2: 'keypad-2',
    pygame.K_KP3: 'keypad-3',
    pygame.K_KP4: 'keypad-4',
    pygame.K_KP5: 'keypad-5',
    pygame.K_KP6: 'keypad-6',
    pygame.K_KP7: 'keypad-7',
    pygame.K_KP8: 'keypad-8',
    pygame.K_KP9: 'keypad-9',
    pygame.K_KP_DIVIDE: 'keypad divide',
    pygame.K_KP_ENTER: 'keypad enter',
    pygame.K_KP_EQUALS: 'keypad equals',
    pygame.K_KP_MINUS: 'keypad minus',
    pygame.K_KP_MULTIPLY: 'keypad asterisk',
    pygame.K_KP_PERIOD: 'keypad full stop',
    pygame.K_KP_PLUS: 'keypad plus',
    pygame.K_AMPERSAND: '&',
    pygame.K_ASTERISK: '*',
    pygame.K_AT: '@',
    pygame.K_BACKQUOTE: '`',
    pygame.K_BACKSLASH: '\\',
    pygame.K_CARET: '^',
    pygame.K_COLON: ':',
    pygame.K_COMMA: ',',
    pygame.K_DOLLAR: '$',
    pygame.K_EQUALS: '=',
    pygame.K_EXCLAIM: '!',
    pygame.K_GREATER: '>',
    pygame.K_LESS: '<',
    pygame.K_HASH: '#',
    pygame.K_LEFTBRACKET: '[',
    pygame.K_LEFTPAREN: '(',
    pygame.K_MINUS: '-',
    pygame.K_PERIOD: '.',
    pygame.K_PLUS: '+',
    pygame.K_QUOTE: "'",
    pygame.K_RIGHTBRACKET: ']',
    pygame.K_RIGHTPAREN: ')',
    pygame.K_SEMICOLON: ';',
    pygame.K_SLASH: '/',
    pygame.K_UNDERSCORE: '_'
}

REVERTKEYBOARD = {v: k for k, v in NAMEKEYBOARD.items()}

TRANSLATEPUNCTUATION = {
    'backquote': '`',
    'backslash': '\\',
    'caret': '^',
    'colon': ':',
    'comma': ',',
    'dollar': '$',
    'equals': '=',
    'exclaim': '!',
    'greater': '>',
    'less': '<',
    'hash': '#',
    'leftbracket': '[',
    'leftparen': '(',
    'minus': '-',
    'period': '.',
    'plus': '+',
    'quote': "'",
    'rightbracket': ']',
    'rightparen': ')',
    'semicolon': ';',
    'slash': '/',
    'underscore': '_'
}


class KeyboardState:
    def __init__(self):
        '''init a view of the keyboard'''
        self._key = []

    def duplicate(self):
        '''Return a new copy of the key states'''
        new_keys = []
        for key in self._key:
            new_keys.append(key)
        state_cpy = KeyboardState()
        state_cpy.set_keyboard_state(new_keys)
        return state_cpy

    def set_keyboard_state(self, keyboard_state):
        '''Initialize the keyboard'''
        self._key = keyboard_state

    def set_state(self, key, state):
        '''update the keyboard'''
        states = list(self._key)
        states[key] = state
        self._key = tuple(states)

    def get_state(self, key):
        """Return the state of a specific key"""
        try:
            return self._key[key]
        except IndexError:
            return None

class Keyboard:
    def __init__(self, keyboard_state, config):
        '''initialize the keyboard
        we need a keyboard state and the config file
        '''
        self.trad = {}
        for key, value in config.items('keymap'):
            # in a config file the ":" and the ";" are very difficult to parse
            # for config.parser. We help him a little.
            if value in TRANSLATEPUNCTUATION:
                value = TRANSLATEPUNCTUATION[value]
            if key in TRANSLATEPUNCTUATION:
                key = TRANSLATEPUNCTUATION[key]
            self.trad[key] = value

        # want to map the keyboard ?
        self.use_keymap = config.getboolean('general', 'use_keymap')
        # pseudo screenshot of the keyboard
        self.current_keyboard = keyboard_state
        # previous state of the keyboard
        self.previous_keyboard = keyboard_state

        # get the current state of the keyboard
        self.current_keyboard.set_keyboard_state(pygame.key.get_pressed())

        self.text_entered = []

    def translate(self, key):
        if key in self.trad and self.use_keymap:
            return REVERTKEYBOARD[self.trad[key]]
        else:
            return REVERTKEYBOARD[key]

    def key_pressed(self, key):
        '''we check if a key is pressed'''
        return self.current_keyboard.get_state(self.translate(key))

    def is_typed(self, key):
        '''Return True if the key has changed'''
        return self.previous_keyboard.get_state(self.translate(key)) and (not
               self.current_keyboard.get_state(self.translate(key)))

    def update(self):
        '''Update the state of the keyboard'''
        keys = pygame.key.get_pressed()
        self.previous_keyboard = self.current_keyboard.duplicate()
        self.current_keyboard.set_keyboard_state(keys)

        # Only get the keybord event
        events = pygame.event.get((pygame.KEYDOWN))
        self.text_entered = []
        for event in events:
            if event.type == pygame.KEYDOWN:
                # We don't want tabulation/return character (no printable)
                if event.unicode and event.key > 32 and event.key is not 127:
                    if event.unicode in self.trad and self.use_keymap:
                        self.text_entered.append(self.trad[event.unicode])
                    else:
                        self.text_entered.append(event.unicode)

    def isUnicode(self):
        '''The submitted key is unicode ?'''
        if self.text_entered:
            return True
        return False

    def get_unicode(self):
        '''return the first input key'''
        return self.text_entered[0]
