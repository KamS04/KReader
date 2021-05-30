# So like this is just a very crude version
# of what I want the final to be
# the final should be cooler with more 
# customizability (check Tachiyomi for references)
# but that takes time to dev so for now this is all I can do
# its gonna be a webtoon/vertical scroll type thing
# without any optimizations
# just a single gridlayout with all the pages loaded as a single strip

from typing import List, Tuple

from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import BooleanProperty, ObjectProperty, StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.label import Label
from kivy.app import App

import os
from functools import partial
from time import sleep
from io import BytesIO

from ...classes import chapter, page
from .. import constants
from ..utils import asynctask
from ..widgets.image import AImage


class PageWidget(AImage):
    pass


class ReaderScreen(MDScreen):
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'reader_screen.kv')
    loading_meta: bool = BooleanProperty(False)
    pages_grid: MDGridLayout = ObjectProperty()
    _ask_query = 0
    _pages_get_task = None
    _images_get_task = None

    def show_chapter(self, chapter: chapter.Chapter):
        self.loading_meta = True
        self._ask_query += 1
        self._pages_get_task = asynctask.AsyncTask(chapter.get_pages, partial(self.receive_pages, self._ask_query))
        self._pages_get_task.start()
    
    def receive_pages(self, query_id: int, result: List[page.Page], time_delta):
        if self._ask_query == query_id:
            print(len(result), 'pages found')
            self.loading_meta = False
            pages_to_load: List[Tuple[page.Page, PageWidget]] = []
            result.sort(key=lambda i: i.number)
            for page_meta in result:
                image = PageWidget()
                self.pages_grid.add_widget(image)
                pages_to_load.append((page_meta, image))
            
            self._images_get_task = asynctask.AsyncTask(partial(self.load_images, query_id, pages_to_load), None)
            self._images_get_task.start()
    
    def load_images(self, query_id: int, pages_to_load: List[Tuple[page.Page, PageWidget]]):
        if self._ask_query == query_id:
            for page_meta, widget in pages_to_load:
                if self._ask_query != query_id:
                    break
                image, ext = page_meta.get_image()
                if image is None:
                    print(page_meta.number, 'could not be loaded')
                Clock.schedule_once(partial(self.display_image, image, ext, widget), 0)
                # This sleep call may seem uneccessary but it is required
                # If you try to show too many images in 1 frame it doesn't work, Some error with the scheduler mayber?
                # This sleep call slows it down, so that everything works
                sleep(0.5)
            print('all pages loaded')
    
    def display_image(self, image: BytesIO, ext: str, widget: AImage, *args):
        if widget is not None:
            widget.load_image(image, ext)

    def go_back_to_manga_screen(self, *args):
        if self._pages_get_task is not None:
            self._pages_get_task.cancel_task()
        if self._images_get_task is not None:
            self._images_get_task.cancel_task()
        
        childs = []
        for child in self.pages_grid.children:
            childs.append(child)
        for child in childs:
            self.pages_grid.remove_widget(child)
        
        Clock.schedule_once(lambda *args: App.get_running_app().go_back_to_manga_screen(), 0.1)


Builder.load_file(ReaderScreen.kv_file)

