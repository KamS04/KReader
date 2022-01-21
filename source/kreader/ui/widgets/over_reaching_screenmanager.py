from kivy.uix.screenmanager import ScreenManager, CardTransition
from kivy.properties import ObjectProperty

from .loading import LoadingBar
from ..constants import over_names

from kivy.clock import Clock


class OverReachingScreenManager(ScreenManager):
    user_input_screen = ObjectProperty()
    last_screen = None

    def start_user_input_cycle(self, widget_to_display):
        self.transition = CardTransition()
        self.direction = 'right'
        self.last_screen = self.current

        if self.user_input_screen.children:
            self.user_input_screen.remove_widget(self.user_input_screen.children[0])
        
        self.user_input_screen.add_widget(LoadingBar())
        self.current = over_names.uinput
        def load_widget(*args):
            self.user_input_screen.remove_widget(self.user_input_screen.children[0])
            self.user_input_screen.add_widget(widget_to_display)
        
        Clock.schedule_once( load_widget, 0.1)

    def close_user_input_cycle(self):
        self.user_input_screen.remove_widget(self.user_input_screen.children[0])
        self.transition = CardTransition(mode='pop')
        self.current = self.last_screen if self.last_screen else over_names.main
        self.last_screen = None

