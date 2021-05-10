from kivy.lang.builder import Builder
from kivy.properties import ListProperty, ColorProperty

from kivymd.uix.label import MDLabel

import os
from .. import constants

def with_margin(num1, num2, margin) -> bool:
    return not (num1 > num2 * (margin + 1) or num1 < num2 * (margin + 1))


class BLabel(MDLabel):
    background_color = ColorProperty()
    background_radius = ListProperty([0, 0, 0, 0])
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'label.kv')


Builder.load_file(BLabel.kv_file)