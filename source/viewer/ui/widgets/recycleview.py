from kivy.lang.builder import Builder
from kivy.uix.recycleview import RecycleView

import os

from .. import constants
from .loading_bar import LoadingBar


class ARecycleView(LoadingBar, RecycleView):
    pass