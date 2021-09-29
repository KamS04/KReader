from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from ..widgets.scoped_widget import ScopedWidget
from ... import source_utils
from ...source_utils import user_input
from ...utils import sources

import os
import asyncio
from functools import partial

KV = '''
#:import LabelButton kreader.ui.widgets.button.LabelButton
#:import constrain kreader.ui.utils.constrain
#:import hex kivy.utils.get_color_from_hex
#:import MarginBackground kreader.ui.widgets.background.MarginBackground
#:import Window kivy.core.window.Window
#:import LoadingBar kreader.ui.widgets.loading.LoadingBar

<CWidget@LoadingBar>:
    bar_color: app.pallete.dark_background

<SourcesScreen>:
    FloatLayout:

        ScrollView:
            size_hint: 1, 1
            pos_hint: { 'center_x': 0.5, 'center_y': 0.5 }
            
            GridLayout:
                cols: 1
                size_hint: 1, None
                height: max(self.minimum_height, Window.size[1])

                Widget:
                    size_hint: 1, None
                    height: 10

                Label:
                    text: 'Installed'
                    font_size: 22
                    color: app.pallete.black
                    height: constrain(root.height * .1, 24, 50)
                    size_hint_y: None
                    halign: 'left'
                    text_size: self.size
                    padding: 15, 0
                    valign: 'center'
                
                MarginBackground:
                    size_hint_y: None
                    height: 2
                    background_color: hex('#2e2e2e')
                    margin_x: 7
                
                CWidget:
                    size_hint_y: None
                    height: 150
                
                Label:
                    text: 'Available'
                    font_size: 22
                    color: app.pallete.black
                    height: constrain(root.height * .1, 24, 59)
                    size_hint_y: None
                    halign: 'left'
                    text_size: self.size
                    padding: 15, 0
                    valign: 'center'
                
                MarginBackground:
                    size_hint_y: None
                    height: 2
                    background_color: hex('#2e2e2e')
                    margin_x: 7

        LabelButton:
            size_hint: None, None
            height: constrain(root.width * .1, 50, 80)
            width: constrain(root.width * .3, 160, 320)
            text: 'Install from Zip'
            font_size: 18
            normal_color: app.pallete.accent
            down_color: app.pallete.main
            pos_hint: { 'right': 1, 'y': 0}
            on_press:
                root.install_from_zip()
'''

last_used_directory_key = 'last_directory_for_zipped_packages'



class SourcesScreen(Screen, ScopedWidget):
    def install_from_zip(self):
        prefs = source_utils.get_prefs()
        last_path = prefs.get(last_used_directory_key, '~/Downloads')
        path = user_input.choose_file('zipfile *.zip', title="Select Zipped Plugin Package", initial_dir=last_path)
        if os.path.exists(path) and path.split(os.path.extsep)[-1] == 'zip':
            used_dir = os.path.dirname(path)
            prefs.edit[last_used_directory_key] = used_dir
            prefs.dump_changes()
            asyncio.create_task(sources.SOURCEMANAGER.install_from_zip(path))

Builder.load_string(KV)
