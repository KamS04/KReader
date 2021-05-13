from kivy.lang.builder import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.app import App
from kivy.properties import ObjectProperty, NumericProperty

import os

from ...classes.manga import Manga
from .. import constants


class MangaWidget(ButtonBehavior, FloatLayout):
    manga: Manga = ObjectProperty()
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'manga.kv')
    margin = NumericProperty(40)
    border_size = NumericProperty(2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'manga' in kwargs.keys():
            self.chapter = kwargs['manga']
    
    def on_press(self, *args):
        if self.manga is not None:
            App.get_running_app().show_manga(self.manga)


Builder.load_file(MangaWidget.kv_file)