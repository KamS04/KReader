from typing import List, Tuple

from io import BytesIO

from . import chapter


class Manga:
    def __init__(self, title: str, authors: List[str], alt_titles: List[str], status: int, uri: str):
        self.title = title
        self.authors = authors
        self.alt_titles = alt_titles
        self.status = status
        self.uri = uri

    def get_chapters(self) -> List['chapter.Chapter']:
        ''' Returns a list of chapters associated with this Manga '''
        pass

    def get_cover_image(self) -> Tuple[BytesIO, str]:
        ''' Gets the cover image of this Manga '''
        pass

    def from_uri(uri: str) -> 'Manga':
        ''' Creates a manga from a specified URI '''
        pass

