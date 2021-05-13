from kivy.lang.builder import Builder
from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty

import os

from ...classes.chapter import Chapter
from .. import constants


class ChapterWidget(ButtonBehavior, Widget):
    chapter: Chapter = ObjectProperty()
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'chapter.kv')
    margin = NumericProperty(40)
    border_size = NumericProperty(2)
    divider = NumericProperty(15)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'chapter' in kwargs.keys():
            self.chapter = kwargs['chapter']
    
    def on_press(self, *args):
        if self.chapter is not None:
            App.get_running_app().show_chapter(self.chapter)


Builder.load_file(ChapterWidget.kv_file)

