from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

KV = '''
#:import markup kivy.core.text.markup
#:import Background kreader.ui.widgets.background.Background

<LogoWidget>:
    height: 120
    size_hint_y: None
    Label:
        size_hint: .9, .9
        pos_hint: { 'center_x': .5, 'center_y': .5 }
        text: '[b]KReader[/b]'
        font_size: 55
        markup: True
        color: 0, 0, 0, 1
    
    Label:
        size_hint: .9, .9
        pos_hint: { 'center_x': .5, 'center_y': .5 }
        text: '[b]KReader[/b]'
        font_size: 52
        markup: True
    
    Background:
        background_color: app.pallete.main
        size_hint: .95, None
        height: 2
        pos_hint: { 'center_x': .5, 'top': .05 }
'''

class LogoWidget(FloatLayout):
    pass

Builder.load_string(KV)
