from typing import List

from . import manga

class Source:
    name: str = 'source_name'

    def choose() -> str:
        ''' Do whatever is required to choose a uri '''
        pass

    def get(uri: str) -> 'manga.Manga':
        ''' Turn the uri from choose() into a Manga object '''
        pass
    
    def search(query: str) -> List['manga.Manga']:
        ''' Search for Manga '''
        pass
