from typing import Any, Tuple
from io import BytesIO

from . import chapter

class Page:
    def __init__(self, number: int, chapter: 'chapter.Chapter', data: Any = None):
        self.number = number
        self.chapter = chapter
        self.data = data

    def get_image(self) -> Tuple[BytesIO, str]:
        ''' Returns the Image to be displayed as a page '''
        pass