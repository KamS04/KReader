from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty, ObjectProperty

KV = '''
<Foreground>:
    canvas.after:
        Color:
            rgba: self.foreground_color
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: root.radius

<MarginForeground>:
    canvas.after:
        Color:
            rgba: self.foreground_color
        RoundedRectangle:
            size: self.size[0] - self._margin_left - self._margin_right, self.size[1] - self._margin_top - self._margin_bottom
            pos: self.pos[0] + self.margin_left, self.pos[1] + self._margin_bottom
            radius: root.radius

<Border>:
    canvas.after:
        Color:
            rgba: self.border_color
        Line:
            points: [ self.pos[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1] + self.size[1], self.pos[0], self.pos[1] + self.size[1], self.pos[0], self.pos[1] ]
'''


class Foreground(Widget):
    foreground_color = ListProperty([0, 0, 0, 0])
    radius = ListProperty([0])


class MarginForeground(Widget):
    foreground_color = ListProperty([0, 0, 0, 0])
    radius = ListProperty([0])
    margin = ListProperty([0, 0, 0, 0])
    margin_x = ListProperty([0, 0])
    margin_y = ListProperty([0, 0])
    _margin_left = NumericProperty(0)
    _margin_right = NumericProperty(0)
    _margin_top = NumericProperty(0)
    _margin_bottom = NumericProperty(0)

    def on_margin(self, instance, new_margin):
        l_m = len(new_margin)
        if l_m == 4:
            self._margin_left, self._margin_top, self._margin_right, self._margin_bottom = new_margin
        elif l_m == 2:
            self.margin_x, self.margin_y = new_margin
        else:
            raise ValueError('New margin must be 2 or 4 integer values')
    
    def on_margin_x(self, instance, new_margin):
        if isinstance(new_margin, int):
            self._margin_left = self._margin_right = new_margin
        elif len(new_margin) == 2:
            self._margin_left, self._margin_right = new_margin
        else:
            raise ValueError('Margin X must be 2 or 1 integer values')
    
    def on_margin_y(self, instance, new_margin):
        if isinstance(new_margin, int):
            self._margin_top = self._margin_bottom = new_margin
        elif len(new_margin) == 2:
            self._margin_top, self._margin_bottom = new_margin
        else:
            raise ValueError('Margin Y must be 2 or 1 integer values')


class ForegroundBorder(Widget):
    border_color = ListProperty([0, 0, 0, 1])
    border_width = NumericProperty(1)

Builder.load_string(KV)
