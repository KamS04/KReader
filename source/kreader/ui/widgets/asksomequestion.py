from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.lang.builder import Builder

KV = '''
#:import LabelButton kreader.ui.widgets.button.LabelButton

<YesNo>:
    Label:
        size_hint: 1, .8
        text: root.message
        pos_hint: { 'x': 0, 'top': 1 }
    GridLayout:
        size_hint: 1, .2
        pos_hint: { 'x': 0, 'y': 0 }
        cols: 2
        spacing: 5, 0

        LabelButton:
            text: root.p_label
            on_release:
                root.dispatch('on_positive')
        
        LabelButton:
            text: root.n_label
            on_release:
                root.dispatch('on_negative')
'''


class YesNo(FloatLayout):
    message = StringProperty('Yes or no?')
    p_label = StringProperty('Yes')
    n_label = StringProperty('No')

    def __init__(self, **kwargs):
        super(YesNo, self).__init__(**kwargs)
        self.register_event_type('on_positive')
        self.register_event_type('on_negative')

    def on_positive(self):
        '''Fired on positive selection'''

    def on_negative(self):
        '''Fired on negative selection'''


def askyesno(title, message, p_label, n_label, on_positive, on_negative):
    content = YesNo(message=message, p_label=p_label, n_label=n_label)
    popup = Popup(title=title, content=content, size_hint=(0.5, 0.5), auto_dismiss=False)
    
    def _positive(instance):
        popup.dismiss()
        if on_positive:
            Clock.schedule_once(on_positive, 0)
    
    def _negative(instance):
        popup.dismiss()
        if on_negative:
            Clock.schedule_once(on_negative, 0)
    
    content.bind(on_positive=_positive, on_negative=_negative)
    popup.open()


Builder.load_string(KV)
