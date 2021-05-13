from kivy.lang.builder import Builder
from kivy.properties import ListProperty, ColorProperty, NumericProperty
from kivymd.uix.label import MDLabel

import os
from .. import constants

def with_margin(num1, num2, margin) -> bool:
    return not (num1 > num2 * (margin + 1) or num1 < num2 * (margin + 1))


KV_FILE = os.path.join( os.getenv(constants.KV_FOLDER), 'label.kv')

class BLabel(MDLabel):
    background_color = ColorProperty()
    background_radius = ListProperty([0, 0, 0, 0])
    kv_file = KV_FILE

class WrappingLabel(BLabel):
    margin = NumericProperty(0)
    kv_file = KV_FILE

Builder.load_file(KV_FILE)