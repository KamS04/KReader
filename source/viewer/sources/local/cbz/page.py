import os
from typing import Any, Tuple

from io import BytesIO
import os

from ....classes import page
from . import chapter


class CBZPage(page.Page):
    def __init__(self, number: int, chapter: 'chapter.CBZChapter', data: Any):
        super().__init__(number, chapter, data)
        self.zip_entry: str = data['zip_entry']
    
    def get_image(self) -> Tuple[BytesIO, str]:
        data = BytesIO(self.chapter.open_file().read(self.zip_entry))
        ext = os.path.basename(self.zip_entry).split(os.path.extsep)[-1]
        return data, ext

