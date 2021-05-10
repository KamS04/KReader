from typing import Any, List, Dict

from . import manga
from . import page


class Chapter:
    def __init__(self, manga: 'manga.Manga', title: str, groups: str, chapter_num: float, language: str, uri: str):
        self.manga = manga
        self.title = title
        self.groups = groups
        self.chapter_num = chapter_num
        self.uri = uri
        self.language = language

    def get_pages() -> List['page.Page']:
        '''Returns a List of Pages '''
        pass

    def from_uri(uri: str, manga: 'manga.Manga', metadata: Dict[Any, Any]) -> 'Chapter':
        ''' Creates a chapter from specified uri '''
        pass

