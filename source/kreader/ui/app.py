from kivymd.app import MDApp
from kivy.lang import Builder

import threading
import os

from ..utils.preferences import PreferencesManager
from .. import source_utils
from .thread_controller import LocalThreadController

from . import constants

def get_prefs(config_file):
    prefs = PreferencesManager(config_file)

    if not os.path.exists(config_file):
        from .default_config import DEFAULT_PREFS
        prefs.direct_dump(DEFAULT_PREFS)
    
    return prefs

DEBUG = bool( os.getenv(constants.DEBUG_KEY) )

FILE_PATH = os.path.abspath(__file__)
BASE_FOLDER = os.path.dirname(FILE_PATH)
KV_FOLDER = os.path.join(BASE_FOLDER, 'kv')

os.environ[constants.KV_FOLDER] = KV_FOLDER

MAIN_KV_FILE = os.path.join(KV_FOLDER, 'main.kv')

CONFIG_FILE_PATH = os.getenv(constants.CONFIG_KEY)
print('config', CONFIG_FILE_PATH)

class KReader(MDApp):
    kv_file = MAIN_KV_FILE

    def build(self):
        return Builder.load_file(self.kv_file)

    def on_start(self):
        self._prefs = get_prefs(CONFIG_FILE_PATH)
        source_utils.get_prefs = lambda: self.prefs # Now everyone can acces the Preferences
        self.thread_manager = LocalThreadController(DEBUG)
        self.thread_manager.start_manager()
    
    @property
    def prefs(self):
        with threading.Lock():
            return self._prefs

    def get_color(self, colour_name):
        return self.prefs.colours[colour_name]

# No __name__ == __main__ because this file should never be
# ran directly, it needs environment variables
# that must be set outside of this file