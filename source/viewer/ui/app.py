from typing import List

import tkinter as tk
from tkinter import messagebox

import kivy
#kivy.require('2.0.0')

from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.uix.screenmanager import SlideTransition
from kivy.network.urlrequest import UrlRequest

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


class Version:
    def __init__(self, version: str):
        self.big, self.small, self.patch = [ int(part) for part in version.split('.') ]

    def __lt__(self, other: 'Version'):
        if self.big == other.big:
            if self.small == other.small:
                return self.patch < other.patch
            return self.small < other.small
        return self.big < other.big
    
    def __gt__(self, other: 'Version'):
        if self.big == other.big:
            if self.small == other.small:
                return self.patch > other.patch
            return self.small > other.small
        return self.big > other.big
    
    def __eq__(self, other: 'Version'):
        return self.big == other.big and self.small == other.small and self.patch == other.patch


_VERSION = Version('0.1.0')
_VERSION_PAGE = 'https://kams04.github.io/KReader/'


class KReader(MDApp):
    kv_file = MAIN_KV_FILE

    resources = os.path.join(BASE_FOLDER, 'res')
    images = os.path.join(resources, 'imgs')

    def get_debug(self) -> bool:
        return DEBUG

    def get_image(self, file_name):
        return os.path.join(self.images, file_name)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pallete = ColorPallete()
    
    def build(self):
        return Builder.load_file(self.kv_file)
    
    def on_start(self):
        self.manga_info_screen = self.root.ids['manga_info_screen']
        self.home_screen = self.root.ids['home_screen']
        self.reader_screen = self.root.ids['reader_screen']
        self.source_screen = self.root.ids['source_screen']
        UrlRequest(_VERSION_PAGE, on_success=self.check_version, on_error=lambda *args: print('Checking for updates failed'))
        return super().on_start()

    def check_version(self, request: UrlRequest, result: str):
        newest = Version(result)
        if _VERSION == newest:
            print('On latest version')
            return
        if _VERSION < newest:
            title = 'Update'
            message = 'Update available. Check the github repository.'
        else:
            title = 'Beta'
            message = 'You are on a non release version. Errors may occur.'
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        messagebox.showinfo(title, message)
        try:
            root.destroy()
        except:
            pass

    def clamp(self, value, min_value, max_value):
        return max(min(value, max_value), min_value)

    def get_sources(*args) -> List[source.Source]:
        return SOURCES

    def show_manga(self, manga: manga.Manga, *args):
        if manga is not None:
            if DEBUG: print(manga.title)
            self.source_screen.cancel_search()
            self.manga_info_screen.load_manga(manga)
            self.root.transition = SlideTransition(direction='left')
            self.root.current = self.manga_info_screen.name

    def go_back_to_manga_screen(self, *args):
        self.root.transition = SlideTransition(direction='right')
        self.root.current = self.manga_info_screen.name

    def show_source(self, selected_source: source.Source, *args):
        self.source_screen.set_source(selected_source)
        self.go_to_sources_screen()

    def switch_to_sources_screen(self, *args):
        self.root.transition = SlideTransition(direction='right')
        self.root.current = self.source_screen.name
    
    def go_to_sources_screen(self, *args):
        self.root.transition = SlideTransition(direction='left')
        self.root.current = self.source_screen.name

    def show_chapter(self, chapter: chapter.Chapter, *args):
        print('Showing', chapter.title)
        self.reader_screen.show_chapter(chapter)
        self.root.transition = SlideTransition(direction='left')
        self.root.current = self.reader_screen.name

    def go_back_home(self, *args):
        self.root.transition = SlideTransition(direction='right')
        self.root.current = self.home_screen.name

