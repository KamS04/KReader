from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.properties import ListProperty, BooleanProperty, NumericProperty
from kivy.animation import Animation

KV = '''
<LoadingBar>:
    canvas.after:
        Color:
            rgba: self.bar_background_color if self.is_loading else (0, 0, 0, 0)
        Rectangle:
            size: self.size
            pos: self.pos
        Color:
            rgba: self.bar_color if self.is_loading else (0, 0, 0, 0)
        PushMatrix
        Rotate
            angle: self._rotation_angle
            origin: self.center
        Line:
            width: self.bar_width
            circle: self.center_x, self.center_y, self.bar_radius, 0, self.bar_angle
        PopMatrix
'''


class LoadingBar(Widget):
    bar_color = ListProperty([0, 0, 0, 1])
    bar_background_color = ListProperty([0, 0, 0, 0])
    is_loading = BooleanProperty(True)
    _rotation_angle = NumericProperty(0)
    bar_width = NumericProperty(4)
    bar_radius = NumericProperty(35)
    bar_angle = NumericProperty(270)
    _animation: Animation = None

    def on_kv_post(self, base_widget):
        self.on_is_loading(self, self.is_loading)

    def on_is_loading(self, instance, is_loading):
        if is_loading:
            self._start_animating()
        else:
            self._stop_loading()
    
    def _start_animating(self):
        self._rotation_angle = 0
        self.animate()
    
    def start_loading(self):
        self.is_loading = True

    def stop_loading(self):
        self.is_loading = False

    def _stop_loading(self):
        if self._animation is not None:
            self._animation.cancel(self)
            self._animation = None
    
    def animate(self, old_animation=None, object_being_animated=None):
        self._animation = Animation(_rotation_angle=self._rotation_angle-360, duration=2)
        self._animation.repeat = True
        self._animation.bind(on_complete=self.animate)
        self._animation.start(self)

Builder.load_string(KV)
