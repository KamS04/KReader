from typing import List


class NamedTupleLikeString:
    def __str__(self):
        return self.__class__.__name__ + '(' + ', '.join( f'{member}={value}' for member, value in vars(self).items() )


class Manga(NamedTupleLikeString):
    title: str = ''
    authors: List[str] = []
    artists: List[str] = []
    alt_titles: List[str] = []
    status: int = 0
    uri: str = ''


class Chapter(NamedTupleLikeString):
    manga: 'Manga' = None
    title: str = ''
    groups: List[str] = []
    chapter_num: float = 0
    uri: str = ''
    language: int = 0
