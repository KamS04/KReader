from collections import namedtuple

MangaBundle = namedtuple('MangaBundle', 'manga_id source_key manga chapters')
ChapterBundle = namedtuple('ChapterBundle','chapter_id chapter')

RawMangaBundle = namedtuple('RawMangaBundle', 'manga_id source_key manga_data')
RawChapterBundle = namedtuple('RawChapterBundle', 'chapter_id manga_id read chapter_data')
