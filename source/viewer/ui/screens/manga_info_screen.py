from typing import Tuple, List

from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.animation import Animation
from kivy.app import App
from kivymd.uix.screen import MDScreen

import os
from io import BytesIO
from functools import partial

from ...classes import chapter, manga, languages
from .. import constants
from ..utils import asynctask
from ..widgets.image import AImage
from ..widgets.recycleview import ARecycleView
from ..widgets.loading_bar import LoadingBar

MIN_SIZE = (168.0, 224.0)
MAX_SIZE = (282.3, 376.40000000003)


class MangaInfoScreen(MDScreen):
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'manga_info_screen.kv')
    cover_image: AImage = ObjectProperty()
    chapters_recycleview: ARecycleView = ObjectProperty()
    loading_bar: LoadingBar = ObjectProperty()
    selected_manga = ObjectProperty(None)
    anim: Animation = None
    _chapters_task: asynctask.AsyncStreamTask = None
    _chapters_query_id = 0
    _chapters: List[chapter.Chapter] = []

    def get_cover_image_size(self, width: int):
        cx = width * 0.3
        cy = width * 0.4
        if cx > MAX_SIZE[0] or cy > MAX_SIZE[1]:
            return MAX_SIZE
        if cx < MIN_SIZE[0] or cy < MIN_SIZE[0]:
            return MIN_SIZE
        return cx, cy
    
    def on_kv_post(self, base_widget):
        self.cover_image.stop_loading()
        self.loading_bar.stop_loading()
        return super().on_kv_post(base_widget)
    
    def load_manga(self, manga: manga.Manga):
        print('loading', manga.title)
        self.cancel_chapters()
        self.cover_image.reset()
        self.cover_image.start_loading()
        self.loading_bar.start_loading()
        self.selected_manga = manga

        self._chapters = []
        self._chapters_query_id += 1
        self._chapters_task = asynctask.AsyncStreamTask(manga.get_chapters, on_update=partial(self.show_chapters, self._chapters_query_id), on_finish=self.finish_chapters)
        self._chapters_task.start()
        asynctask.AsyncTask(manga.get_cover_image, self.show_cover_image).start()
    
    def filter(self, chapters: List[chapter.Chapter]) -> List[chapter.Chapter]:
        return [ chapter for chapter in chapters if chapter.language == languages.ENGLISH ]

    def show_chapters(self, query_id: int, chapters: List[chapter.Chapter], time_delta: float) -> List[chapter.Chapter]:
        if query_id == self._chapters_query_id:
            filtered_chapters = [ {'chapter': chapter} for chapter in self.filter(chapters) ]
            print('showing', len(filtered_chapters), 'chapters')
            self._chapters += filtered_chapters
            self.chapters_recycleview.data = self._chapters
    
    def finish_chapters(self, *args):
        self.loading_bar.stop_loading()

    def show_cover_image(self, image_data: Tuple[BytesIO, str], time_delta: float):
        if image_data is not None:
            self.cover_image.load_image(*image_data)
        else:
            print('Image is None')
            self.cover_image.stop_loading()
    
    def cancel_chapters(self, *args):
        if self._chapters_task is not None:
            self._chapters_task.cancel_task()
            self._chapters_query_id += 1
            self._chapters_task = None

    def go_back_to_sources(self, *args):
        # here you can un load any mangas and stuff
        # for now I'm going to keep them cause it's not hurting any body
        # but for optimal performace it would be best to delete the images,
        # chapters and general data that the manga object stored in this screen
        # I am getting rid of the data in the recycleview so that when we come back to this screen
        # it will start fresh
        self.chapters_recycleview.data = []
        self.cancel_chapters()
        App.get_running_app().switch_to_sources_screen()


Builder.load_file(MangaInfoScreen.kv_file)

