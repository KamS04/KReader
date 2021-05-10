import os
from kivy.lang.builder import Builder

from kivymd.uix.gridlayout import MDGridLayout

import os

from .. import constants

KV_FILE = os.path.join( os.getenv(constants.KV_FOLDER), 'gridlayout.kv' )


class SHGridLayout(MDGridLayout):
    kv_file = KV_FILE


class SVGridLayout(MDGridLayout):
    kv_file = KV_FILE


Builder.load_file(KV_FILE)

