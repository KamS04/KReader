from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.uix.behaviors.button import ButtonBehavior
from kivy.uix.image import Image, CoreImage
from kivy.properties import ColorProperty, BooleanProperty, NumericProperty

import os
from io import BytesIO
from PIL import Image as PImage

from .loading_bar import LoadingBar
from .. import constants


class ImageButton(ButtonBehavior, Image):
    pass


class AImage(LoadingBar, ImageButton):
    kv_file = os.path.join( os.getenv(constants.KV_FOLDER), 'image.kv')
    background_color = ColorProperty()
    clickable = BooleanProperty()
    image_bytes: BytesIO = None
    image_ext: str = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def load_image(self, image: BytesIO, ext: str):
        self.image_bytes = image
        self.image_ext = ext
        self.image_bytes.seek(0)
        coreimage = CoreImage(self.image_bytes, ext=self.image_ext)
        self.texture = coreimage.texture
        self.stop_loading()
    
    def reset(self):
        self.texture = None
        self.image_ext = None
        self.image_bytes = None
    
    def on_press(self):
        if self.clickable and self.image_bytes is not None:
            PImage.open(self.image_bytes).show()


Builder.load_file(AImage.kv_file)

