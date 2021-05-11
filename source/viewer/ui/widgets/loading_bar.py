from kivy.lang.builder import Builder
from kivy.uix.widget import Widget
from kivy.animation import Animation
from kivy.properties import BooleanProperty, NumericProperty

import os

from .. import constants


class LoadingBar(Widget):
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'loading_bar.kv')
    loading = BooleanProperty()
    arc_angle = NumericProperty(270)
    arc_width = NumericProperty(4)
    arc_radius = NumericProperty(35)
    angle = NumericProperty(0)
    anim: Animation = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_loading()

    def start_loading(self):
        self.loading = True
        self.start_animating()
    
    def stop_loading(self):
        self.loading = False
        if self.anim is not None:
            self.anim.stop(self)

    def start_animating(self):
        self.angle = 0
        self.arc_angle = 270
        self.animate()

    def animate(self, animation=None, animating_object=None):
        self.anim = Animation(angle=self.angle-360, arc_angle=0 if self.arc_angle == 270 else 270, duration=2)
        self.anim.bind(on_complete=self.animate)
        self.anim.start(self)


Builder.load_file(LoadingBar.kv_file) # with this the kv file will be laoded once the file is imported

