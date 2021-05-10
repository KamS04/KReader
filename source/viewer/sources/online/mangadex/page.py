from typing import Tuple, Any

from io import BytesIO
import os
import requests

from ....classes import page
from . import chapter

class MangaDexPage(page.Page):
    def __init__(self, number: int, chapter: 'chapter.MangaDexChapter', data: Any, server=None, file=None):
        super().__init__(number, chapter, data)
        self.file: str = file if file else self.data['file']
        self.server: str = server if server else self.data['server']
    
    def get_image(self) -> Tuple[BytesIO, str]:
        ext = os.path.basename(self.file).split(os.path.extsep)[-1]
        req = requests.get(self.file_url)
        if req.ok:
            data = BytesIO(req.content)
            return data, ext
        return None, None
    
    @property
    def file_url(self) -> str:
        return f'{self.server}/data/{self.chapter.chapter_hash}/{self.file}'

