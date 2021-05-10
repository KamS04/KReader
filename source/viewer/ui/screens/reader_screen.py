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

    def show_chapter(self, chapter: chapter.Chapter):
        self.loading_meta = True
        asynctask.AsyncTask(chapter.get_pages, self.receive_pages).start()
    
    def receive_pages(self, result: List[page.Page], time_delta):
        print(len(result), 'pages found')
        self.loading_meta = False
        pages_to_load: List[Tuple[page.Page, PageWidget]] = []
        result.sort(key=lambda i: i.number)
        for page_meta in result:
            image = PageWidget()
            self.pages_grid.add_widget(image)
            pages_to_load.append((page_meta, image))
        
        asynctask.AsyncTask(partial(self.load_images, pages_to_load), None).start()
    
    def load_images(self, pages_to_load: List[Tuple[page.Page, PageWidget]]):
        for page_meta, widget in pages_to_load:
            widget.text = str(page_meta.number)
            image, ext = page_meta.get_image()
            if image is None:
                print(page_meta.number, 'could not be loaded')
            Clock.schedule_once(lambda *args: widget.load_image(image, ext), 0)
            # This sleep call may seem uneccessary but it is required
            # If you try to show too many images in 1 frame it doesn't work, Some error with the scheduler mayber?
            # This sleep call slows it down, so that everything works
            sleep(0.5)
        print('all pages loaded')


Builder.load_file(ReaderScreen.kv_file)

