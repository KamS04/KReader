from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock

from .gridlayout import SVGridLayout
from .loading import LoadingBar

from ...utils import sources

KV = '''
#:import hex kivy.utils.get_color_from_hex
#:import MarginBackground kreader.ui.widgets.background.MarginBackground
#:import Background kreader.ui.widgets.background.Background
#:import ImageButton kreader.ui.widgets.button.ImageButton

<SourcesView>:
    padding: 7, 0

<SourceView>:
    size_hint_y: None
    height: max(54, name_label.height + 4)

    GridLayout:
        size_hint: 1, None
        pos_hint: { 'x': 0, 'top': 1 }
        height: max(50, name_label.height)
        cols: 2

        GridLayout:
            cols: 2
            size_hint: 1, None
            pos_hint: { 'center_y': 0.5, 'x': 0 }
            height: self.minimum_height
            padding: 7, 0
            spacing: 5, 0

            Image:
                source: root.icon_image
                size_hint: None, None
                size: 45, 45

            Label:
                id: name_label
                font_size: 18
                text: root.ellipsed_name # "Some text even more text I keep adding text so much text cause its like hopefully good text but I'll keep adding text please let me add more text"
                size_hint: None, None
                # pos_hint: { 'center_y': 0.5, 'x': 0.1 }
                color: app.pallete.black
                halign: 'left'
                text_size: self.size[0], None
                padding_x: 6
                height: max(self.texture_size[1], root.height * 0.9)
        
        GridLayout:
            cols: 2
            size_hint: None, None
            height: 45
            width: 90 + 7 * 2 + 5
            pos_hint: { 'center_y': 0.5, 'right': 1 }
            padding: 7, 0
            spacing: 5, 0

            ImageButton:
                size: 45, 45
                source: app.get_asset_path('/images/settings.png')
                down_tint: app.pallete.button_tint
                radius: 20,
                on_release:
                    root.dispatch('on_settings')


            ImageButton:
                size: 45, 45
                source: app.get_asset_path('/images/delete.png')
                down_tint: app.pallete.button_tint
                radius: 20,
                on_release:
                    root.dispatch('on_uninstall')
    
    MarginBackground:
        size_hint_y: None
        height: 1
        background_color: hex('#aeaeae')
        margin_x: 0
        pos_hint: { 'y': 0, 'x': 0 }
'''


class SourcesView(SVGridLayout, LoadingBar):
    pass


class SourceView(FloatLayout):
    source = ObjectProperty()
    ellipsed_name = StringProperty('')
    icon_image = StringProperty('')

    def __init__(self, **kwargs):
        self.register_event_type('on_uninstall')
        self.register_event_type('on_settings')
        super(SourceView, self).__init__(**kwargs)

    def _update_icon_image(self, *args):
        self.icon_image = sources.SOURCEMANAGER.resolve_asset_path(self.source, self.source.icon)

    def on_source(self, instance, source):
        Clock.schedule_once(self._update_icon_image, 0)
        self.ellipsed_name = source.name if len(source.name) < 30 else source.name[:27] + '...'

    def on_uninstall(self):
        '''Event fires on uninstall event'''

    def on_settings(self):
        '''Event fires on settings event'''


Builder.load_string(KV)