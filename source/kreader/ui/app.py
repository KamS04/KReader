import asyncio
import os

from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.core.window import Window

Window.minimum_height = 400
Window.minimum_width = 540

import threading
import os

from ..utils.cursor import CursorController
from ..thread_sys.lock import LockingObject
from ..utils.preferences import PreferencesManager
from .. import source_utils
from ..utils import sources
from .widgets import asksomequestion

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


class KReader(MDApp):
    kv_file = MAIN_KV_FILE
    
    @staticmethod
    def get_instance() -> 'KReader':
        return APP

    def __init__(self, *args, **kwargs):
        super(KReader, self).__init__(*args, **kwargs)
        self.pallete = Pallete()
        self.cursor_controller = CursorController()

    def on_start(self):
        self.prefs: LockingObject[PreferencesManager] = LockingObject(get_prefs(CONFIG_FILE_PATH))
        source_utils.get_prefs = lambda: self.prefs # Now everyone can acces the Preferences
        def _get_install_dir() -> str:
            with self.prefs as prefs:
                plugin_install_directory = prefs.plugin_install_directory
                if plugin_install_directory is None:
                    plugin_install_directory = os.path.join( os.path.dirname(BASE_FOLDER), 'plugins')
                    prefs.edit.plugin_install_directory = plugin_install_directory
                    prefs.dump_changes()
            return plugin_install_directory
        source_utils.get_install_directory = _get_install_dir
        sources.create_now()
        asyncio.create_task(sources.SOURCEMANAGER.load_sources())

    def get_color(self, colour_name):
        with self.prefs as prefs:
            return prefs.colours[colour_name]
    
    def start_user_input_cycle(self, widget_to_display):
        self.root.start_user_input_cycle(widget_to_display)
    
    def close_user_input_cycle(self):
        self.root.close_user_input_cycle()
    
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.5, 0.5))
        popup.open()
    
    def get_asset_path(self, asset):
        return os.path.abspath(os.path.dirname(__file__) + '/assets' + asset)

    def askyesno(self, title='', message='', p_label='Yes', n_label='No', on_positive=None, on_negative=None):
        asksomequestion.askyesno(title, message, p_label, n_label, on_positive, on_negative)


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