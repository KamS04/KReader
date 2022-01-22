from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.properties import ObjectProperty

from ...classes.source import Source
from ....source import Source

from ..app import KReader
from ..widgets.scoped_widget import ScopedWidget
from ... import source_utils
from ...source_utils import user_input
from ...utils import sources
from ..widgets.source_views import SourceView

import os
import asyncio
from functools import partial

from ...utils import publisher

from .. import handlers

KV = '''
#:import LabelButton kreader.ui.widgets.button.LabelButton
#:import constrain kreader.ui.utils.constrain
#:import hex kivy.utils.get_color_from_hex
#:import MarginBackground kreader.ui.widgets.background.MarginBackground
#:import Background kreader.ui.widgets.background.Background
#:import Window kivy.core.window.Window
#:import SourcesView kreader.ui.widgets.source_views.SourcesView

<SourcesScreen>:
    sources_view: sources_view

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
                
                SourcesView:
                    id: sources_view
                    size_hint_y: None
                    height: 150
                    bar_color: app.pallete.dark_background
                
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
    sources_view = ObjectProperty()

    def on_kv_post(self, base_widget):
        publisher.subscribe(sources.SOURCE_UPDATE_TOPIC, self, self._receive_plugin_message)

    def install_from_zip(self):
        asyncio.create_task(self._install_from_zip())

    async def _install_from_zip(self):
        selected_path = await self._select_path()
        print(selected_path)
        if not selected_path:
            KReader.get_instance().show_popup(title='Error', message='No File Selected')
            return
        
        selected_path = selected_path[0]
        if os.path.exists(selected_path) and selected_path.split(os.path.extsep)[-1] == 'zip':
            await handlers.PROCESSING(lambda: self._save_selected_path(selected_path))
            asyncio.create_task(sources.SOURCEMANAGER.install_from_zip(selected_path))
    
    async def _select_path(self):
        with source_utils.get_prefs() as prefs:
            last_path = prefs.get(last_used_directory_key, '~/Downloads')
        return await user_input.choose_file(('Zip File *.zip', '*.zip'), title='Select Zipped Plugin Package', initial_dir=last_path)

    async def _save_selected_path(self, selected_path):
        used_dir = os.path.dirname(selected_path)
        with source_utils.get_prefs() as prefs:
            prefs.edit[last_used_directory_key] = used_dir
            prefs.dump_changes()
    
    def _receive_plugin_message(self):
        self.sources_view.stop_loading()
        ol_childs = [ i for i in self.sources_view.children ]
        for child in ol_childs:
            self.sources_view.remove_widget(child)
        for source in sources.SOURCEMANAGER.sources:
            widget = SourceView(source=source)
            widget.bind(on_uninstall=partial(self._ask_uninstall, source))
            self.sources_view.add_widget(widget)
        print('stopped loading')
        pass

    def _ask_uninstall(self, source, instance):
        KReader.get_instance().askyesno(title='Uninstall?', message=f'Are you sure you would like to uninstall {source.name}', on_positive=partial(self._uninstall, source))

    def _uninstall(self, source: Source, instance):
        sources.SOURCEMANAGER.uninstall_source(source)


Builder.load_string(KV)
