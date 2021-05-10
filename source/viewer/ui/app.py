from typing import List

import kivy
kivy.require('2.0.0')

from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import SlideTransition

import kivymd
from kivymd.app import MDApp

import os
from functools import partial

from ..classes import manga, chapter, source

# Sources
from ..sources.local.cbz import CBZ
from ..sources.online.mangadex import MangaDex

from . import constants
from .colors import ColorPallete
from .utils import asynctask

DEBUG = True

BASE_FOLDER = os.path.dirname(__file__)
KV_FOLDER = os.path.join(BASE_FOLDER, 'kv')

os.environ[constants.KV_FOLDER] = KV_FOLDER

MAIN_KV_FILE = os.path.join(KV_FOLDER, 'main.kv')

SOURCES: List[source.Source] = [
    CBZ,
    MangaDex
]


class KReader(MDApp):
    kv_file = MAIN_KV_FILE

    resources = os.path.join(BASE_FOLDER, 'res')
    images = os.path.join(resources, 'imgs')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pallete = ColorPallete()
        self.is_selecting = False
        self.is_finding = False
    
    def build(self):
        return Builder.load_file(self.kv_file)
    
    def on_start(self):
        self.manga_info_screen = self.root.ids['manga_info_screen']
        self.sources_screen = self.root.ids['sources_screen']
        self.reader_screen = self.root.ids['reader_screen']
        return super().on_start()

    def clamp(self, value, min_value, max_value):
        return max(min(value, max_value), min_value)

    def get_sources(*args) -> List[source.Source]:
        return SOURCES
    
    def select_from_source(self, source: source.Source):
        if not self.is_selecting and not self.is_finding:
            self.is_selecting = True
            asynctask.AsyncTask(source.choose, partial(self.show_manga_from_uri, source)).start()

    def show_manga_from_uri(self, source: source.Source, uri: str, time_delta: float):
        self.is_selecting = False

        if DEBUG: print(source, 'selected', uri)

        if uri is not None:
            self.is_finding = True
            asynctask.AsyncTask(partial(source.get, uri), self.show_manga).start()
        else:
            print('Erorr, NoneType object returned, uri not selected')
    
    def show_manga(self, manga: manga.Manga, time_delta):
        if manga is not None:
            if DEBUG: print(manga.title)

            self.manga_info_screen.load_manga(manga)
            self.root.transition = SlideTransition(direction='left')
            self.root.current = self.manga_info_screen.name
        self.is_finding = False

    def switch_to_sources_screen(self, *args):
        self.root.transition = SlideTransition(direction='right')
        self.root.current = self.sources_screen.name
    
    def show_chapter(self, chapter: chapter.Chapter):
        print('Showing', chapter.title)
        self.reader_screen.show_chapter(chapter)
        self.root.transition = SlideTransition(direction='left')
        self.root.current = self.reader_screen.name

