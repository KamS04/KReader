from typing import List, Dict, Any

import os
import zipfile

from ....classes import chapter, languages
from .... import sources
from . import manga
from . import page


class CBZChapter(chapter.Chapter):
    accepted_file_types = ('cbz', 'zip')

    def __init__(self, manga: 'manga.CBZManga', name: str, groups: List[str], chapter_num: float, language: str, uri: str):
        super().__init__(manga, name, groups, chapter_num, language, uri)
    
    def get_pages(self) -> List['page.CBZPage']:
        page_names: List[str] = []
        pages: List[page.CBZPage] = []
        file = self.open_file()

        for zipentry in file.filelist:
            if (not zipentry.is_dir() and
                os.path.basename(zipentry.filename).split(os.path.extsep)[-1] in sources.sources.ALLOWED_IMAGE_TYPES):
                page_names.apend(zipentry.filename)
        page_names.sort()
        
        for number, page_name in enumerate(page_names):
            pages.append(page.CBZPage(number + 1, self, {'zip_entry': page_name}))

        file.close()
        return pages

    def from_uri(uri: str, manga: 'manga.CBZManga', metadata: Dict[Any, Any]) -> 'CBZChapter':
        if (os.path.exists(uri) and
            os.path.isfile(uri) and
            os.path.split(uri)[-1].split(os.path.extsep)[-1] in CBZChapter.accepted_file_types):

            meta_keys = metadata.keys()
            name = metadata['name'] if 'name' in meta_keys else os.path.basename(uri)
            groups = metadata['group'] if 'group' in meta_keys else ['No Group']
            chapter_num = metadata['chapter_number']
            language = metadata['language'] if 'language' in meta_keys in meta_keys else languages.ENGLISH

            return CBZChapter(manga, name, groups, chapter_num, language, uri)
        return None
    
    def open_file(self) -> zipfile.ZipFile:
        return zipfile.ZipFile(self.uri)

