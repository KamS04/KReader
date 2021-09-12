import asyncio

from kivymd.app import MDApp
from kivy.lang import Builder

import threading
import os

from ..utils.preferences import PreferencesManager
from .. import source_utils
from ..utils import sources

from .pallete import Pallete

from .constants import app_constants
from . import handlers

def get_prefs(config_file):
    prefs = PreferencesManager(config_file)

    if not os.path.exists(config_file):
        from .default_config import DEFAULT_PREFS
        prefs.direct_dump(DEFAULT_PREFS)
    
    return prefs

DEBUG = bool( os.getenv(app_constants.DEBUG_KEY) )

FILE_PATH = os.path.abspath(__file__)
BASE_FOLDER = os.path.dirname(FILE_PATH)
KV_FOLDER = os.path.join(BASE_FOLDER, 'kv')
PREFERENCE_LOCK = threading.Lock()
APP: 'KReader' = None

os.environ[app_constants.KV_FOLDER] = KV_FOLDER

MAIN_KV_FILE = os.path.join(KV_FOLDER, 'main.kv')

CONFIG_FILE_PATH = os.getenv(app_constants.CONFIG_KEY)
print('config', CONFIG_FILE_PATH)

class KReader(MDApp):
    kv_file = MAIN_KV_FILE

    def __init__(self, *args, **kwargs):
        super(KReader, self).__init__(*args, **kwargs)
        self.pallete = Pallete()

    def build(self):
        return Builder.load_file(self.kv_file)

    def on_start(self):
        self._prefs = get_prefs(CONFIG_FILE_PATH)
        source_utils.get_prefs = lambda: self.prefs # Now everyone can acces the Preferences
        def _get_install_dir() -> str:
            plugin_install_directory = self.prefs.plugin_install_directory
            if plugin_install_directory is None:
                plugin_install_directory = os.path.join( os.path.dirname(BASE_FOLDER), 'plugins')
                self.prefs.edit.plugin_install_directory = plugin_install_directory
                self.prefs.dump_changes()
            return plugin_install_directory
        source_utils.get_install_directory = _get_install_dir
        sources.create_now()
        asyncio.create_task(sources.SOURCEMANAGER.load_sources())


    @property
    def prefs(self) -> PreferencesManager:
        with PREFERENCE_LOCK:
            return self._prefs

    def get_color(self, colour_name):
        return self.prefs.colours[colour_name]

async def main():
    global APP
    try:
        await handlers.initialize_handlers()

        APP = KReader()
        await APP.async_run(async_lib='asyncio')
    except KeyboardInterrupt:
        exit(1)
    
    exit(0)

# No __name__ == __main__ because this file should never be
# ran directly, it needs environment variables
# that must be set outside of this file