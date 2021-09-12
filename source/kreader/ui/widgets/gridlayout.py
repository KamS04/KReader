from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder

from .background import Background

KV = '''
<SVGridLayout>:
    cols: 1
    size_hint_y: None
    height: self.minimum_height

<SHGridLayout>:
    rows: 1
    size_hint_x: None
    width: self.minimum_width
'''

class SVGridLayout(GridLayout, Background):
    pass

class SHGridLayout(GridLayout, Background):
    pass

Builder.load_string(KV)
