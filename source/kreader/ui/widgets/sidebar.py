from kivy.uix.scrollview import ScrollView
from kivy.lang import Builder
from kivy.properties import DictProperty, StringProperty, ObjectProperty

from .button import TogglableButton
from .background import Border

KV = '''
#:import LogoWidget kreader.ui.widgets.logo_widget.LogoWidget
#:import SVGridLayout kreader.ui.widgets.gridlayout.SVGridLayout
#:import Window kivy.core.window.Window

<TabButton>:
    normal_color: app.pallete.main
    selected_color: app.pallete.accent
    size_hint_y: None
    height: 60
    font_size: 18

<SideBarCommunicator>:
    root_grid: root_grid

    SVGridLayout:
        background_color: app.pallete.dark_background
        canvas.before:
            Color:
                rgb: app.pallete.dark_background
            Rectangle:
                size: self.size
                pos: self.pos
        id: root_grid
        height: max(self.minimum_height, Window.size[1])

        LogoWidget:

        Widget:
            height: 20
            size_hint_y: None

'''

class TabButton(TogglableButton, Border):
    pass

class SideBarCommunicator(ScrollView):
    tabs = DictProperty({})
    default = StringProperty('')
    old_tab = None
    selection = StringProperty('')
    root_grid = ObjectProperty(None)

    def on_kv_post(self, base_widget):
        first = None
        for tab in self.tabs.keys():
            tab_button = TabButton(text=tab)
            tab_button.bind(selected=self.selection_changed)
            if tab == self.default:
                first = tab_button
            self.root_grid.add_widget(tab_button)

        if first is not None:
            first.selected = True
    
    def selection_changed(self, tab, selected):
        if selected:
            if self.old_tab is not None:
                self.old_tab.clear()
            self.old_tab = tab
            self.selection = self.tabs[tab.text]
    

Builder.load_string(KV)
