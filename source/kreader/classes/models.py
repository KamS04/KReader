from typing import List


class Manga:
    title: str = ''
    authors: List[str] = []
    artists: List[str] = []
    alt_titles: List[str] = []
    status: int = 0
    uri: str = ''


class Chapter:
    manga: 'Manga' = None
    title: str = ''
    groups: List[str] = []
    chapter_num: float = 0
    uri: str = ''
    language: int = 0
