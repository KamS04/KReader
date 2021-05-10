from typing import List, Generator

from . import manga

class Source:
    name: str = 'source_name'

    def choose() -> str:
        ''' Do whatever is required to choose a uri '''
        pass

    def get(uri: str) -> 'manga.Manga':
        ''' Turn the uri from choose() into a Manga object '''
        pass
    
    def search(query: str) -> Generator[List['manga.Manga'], None, None]:
        ''' Search for Manga '''
        pass
