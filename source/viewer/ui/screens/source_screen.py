# http://api.mangadex.org/manga/000245bf-670e-49c5-af47-1d674a43525c

from typing import List
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.app import App
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivy.uix.recycleview import RecycleView

import os
from functools import partial

from ...classes import source, manga

from .. import constants
from ..widgets.loading_bar import LoadingBar
from ..widgets.gridlayout import SVGridLayout
from ..utils import asynctask

class SourceScreen(MDScreen):
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'source_screen.kv')
    selected_source: source.Source = ObjectProperty(None)
    search_box: MDTextField = ObjectProperty()
    mangas_recycleview: RecycleView = ObjectProperty()
    loading_bar: LoadingBar = ObjectProperty()
    _found_mangas: List[manga.Manga] = []
    
    is_selecting = False
    is_finding = False
    DEBUG = False

    _search_task: asynctask.AsyncStreamTask = None
    query_id = 0

    def on_kv_post(self, base_widget):
        self.DEBUG = App.get_running_app().get_debug()
        self.loading_bar.stop_loading()
        return super().on_kv_post(base_widget)

    def set_source(self, source: source.Source):
        self.selected_source = source

    def go_back_home(self, *args):
        self.search_box.text = ''
        self._found_mangas = []
        self.mangas_recycleview.data = []
        self.cancel_search()
        App.get_running_app().go_back_home()
    
    def choose(self, *args):
        if not (self.is_selecting or self.is_finding or self.selected_source is None):
            self.is_selecting = True
            asynctask.AsyncTask(self.selected_source.choose, partial(self.show_manga_from_uri, self.selected_source)).start()
    
    def show_manga_from_uri(self, source: source.Source, uri: str, time_delta: float):
        self.is_selecting = False

        if self.DEBUG: print(source, 'selected', uri)

        if uri is not None:
            self.is_finding = True
            asynctask.AsyncTask(partial(source.get, uri), App.get_running_app().show_manga).start()
        else:
            print('Erorr, NoneType object returned, uri not selected')

    def search(self, *args):
        self._found_mangas = []
        query = self.search_box.text
        print('searching for', query)
        self.mangas_recycleview.data = []
        if self.selected_source is not None:
            self.cancel_search()
            self._search_task = asynctask.AsyncStreamTask(partial(self.selected_source.search, query), on_update=partial(self.show_found_mangas, self.query_id), on_finish=self.finish_search)
            self._search_task.start()
            self.loading_bar.start_loading()
    
    def cancel_search(self, *args):
        print('cancel')
        if self._search_task is not None:
            self._search_task.cancel_task()
            self.query_id += 1
            self.loading_bar.stop_loading()

    def show_found_mangas(self, query_id: int, mangas: List[manga.Manga], time_delta: float):
        print('id', query_id, self.query_id)
        if query_id == self.query_id:
            self._found_mangas += [ {'manga': manga} for manga in mangas ]
            self.mangas_recycleview.data = self._found_mangas
            print('found', len(self._found_mangas))

    def finish_search(self, *args):
        self.loading_bar.stop_loading()


Builder.load_file(SourceScreen.kv_file)