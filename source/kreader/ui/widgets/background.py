from typing import List
from kivy.uix.widget import Widget
from kivy.lang import Builder
from kivy.properties import ListProperty, NumericProperty

KV = '''
<Background>:
    canvas.before:  
        Color:  
            rgba: self.background_color
        Rectangle:
            size: self.size
            pos: self.pos

<Border>:
    canvas.before:
        Color:
            rgba: self.border_color
        Line:
            points: [ self.pos[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1], self.pos[0] + self.size[0], self.pos[1] + self.size[1], self.pos[0], self.pos[1] + self.size[1], self.pos[0], self.pos[1] ]
'''

class Background(Widget):
    background_color = ListProperty([0, 0, 0, 0])

class Border(Widget):
    border_color = ListProperty([0, 0, 0, 1])
    border_width = NumericProperty(1)

Builder.load_string(KV)
