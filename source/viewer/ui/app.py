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
from .utils import asyntask

DEBUG = True

BASE_FOLDER = os.path.dirname(__file__)
KV_FOLDER = os.path.join(BASE_FOLDER, 'kv')

os.putenv(constants.KV_FOLDER, KV_FOLDER)

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
    
