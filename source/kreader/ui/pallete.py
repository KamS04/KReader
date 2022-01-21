from kivy.utils import get_color_from_hex

class Pallete:
    def __init__(self):
        self.light_background = get_color_from_hex('#EEEEEE')
        self.background_text = get_color_from_hex('#FFFFFF')
        self.main = get_color_from_hex('#0094C6')
        self.black = get_color_from_hex('#000000')
        self.dark_background = get_color_from_hex('#001242')
        self.accent = get_color_from_hex('#005E7C')
        self.darker_background = get_color_from_hex('#000022')
        self.button_tint = get_color_from_hex('#77777744')

