from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.properties import ListProperty, BooleanProperty
from kivy.utils import get_color_from_hex

from .background import Background

class LabelButton(ButtonBehavior, Label, Background):
    down_color = get_color_from_hex('#32a4ce')
    normal_color = get_color_from_hex('#585858')
    disabled_color = get_color_from_hex('#1a1a1a')

    def on_kv_post(self, base_widget):
        self.on_disabled(self, self.disabled)

    def on_state(self, instance, new_state):
        if new_state == 'down':
            self.background_color = self.down_color
        else:
            self.background_color = self.normal_color
    
    def on_disabled(self, instance, disabled):
        if disabled:
            self.background_color = self.disabled_color
        else:
            self.on_state(self, self.state)

class TogglableButton(LabelButton):
    selected_color = get_color_from_hex('#15699e')
    selected = BooleanProperty(False)

    def on_state(self, instance, new_state):
        if not self.selected:
            super(TogglableButton, self).on_state(instance, new_state)
    
    def on_release(self):
        self.selected = True

    def clear(self):
        self.selected = False

    def on_selected(self, instance, selected):
        if selected:
            self.background_color = self.selected_color
        else:
            self.background_color = self.normal_color
