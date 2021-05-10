from typing import List
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRoundFlatButton, MDFlatButton, MDRaisedButton, Button

import os

from ...classes import source

from .. import constants
from ..widgets.gridlayout import SVGridLayout


class SourcesScreen(MDScreen):
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'sources_screen.kv')
    sources_grid: SVGridLayout = ObjectProperty()
    sources: List[source.Source] = []

    def on_kv_post(self, base_widget):
        sources: List[source.Source] = App.get_running_app().get_sources()
        self.sources = sorted(sources, key=lambda source: source.name)

        for idx, source in enumerate(self.sources):
            button = MDRaisedButton(text=source.name, on_press=lambda _, index=idx: self.call_source(index))
            self.sources_grid.add_widget(button)
        
        return super().on_kv_post(base_widget)
    
    def call_source(self, source_index):
        source = self.sources[source_index]
        # print(source.name)

        # here we can either show the sources home page
        # but we don't have that implemented so instead we're just going to ask it to pick a manga

        App.get_running_app().select_from_source(source)


Builder.load_file(SourcesScreen.kv_file)

