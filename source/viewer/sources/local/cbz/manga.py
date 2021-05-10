from typing import Any, Dict, List, Tuple

import os
import json
from io import BytesIO
from ....classes import manga, status
from . import chapter


class CBZManga(manga.Manga):
    ''' Note this Manga type requires you to choose a folder which contains .cbz or .zip files '''

    def get_info_file_path(uri) -> str:
        return os.path.join(uri, 'source_info.json')

    @property
    def info_file_path(self):
        return CBZManga.get_info_file_path(self.uri)

    def __init__(self, name: str, authors: List[str], alt_titles: List[str], status: int, uri: str):
        super().__init__(name, authors, alt_titles, status, uri)

    def get_chapters(self) -> List['chapter.CBZChapter']:
        chapters : List[chapter.CBZChapter] = []
        
        if 'chapters' in self.get_info().keys(): # if chapters listed in source info, use those
            chapters_info = self.get_info()['chapters']            
            for chapter_info in chapters_info:
                chapters.append(chapter.CBZChapter.from_uri(chapter_info['path'], self, chapter_info))
        
        else: # if chapters not listed in source info, scan the directory to find chapters
            chapters_names = []
            
            for item in os.scandir(self.uri):
                if (item.is_file() and 
                    item.name.split(os.path.extsep)[-1] in chapter.CBZChapter.accepted_file_types):
                    chapters_names.append(item.path)
            
            chapters_names.sort(key=lambda i: os.path.basename(i)) # sort the files, using the file name as the key
            for index, chapter_name in enumerate(chapters_names):
                chapters.append(chapter.CBZChapter.from_uri(chapter_name, self, {'chapter-number': index+1}))
        
        return chapters

    def get_cover_image(self) -> Tuple[BytesIO, str]:
        if 'cover_image' in self.get_info().keys():
            image_path = self.get_info()['cover_image']
            ext = os.path.basename(image_path).split(os.path.extsep)[-1]
            return BytesIO(open(image_path)), ext
        return None

    def from_uri(uri: str) -> 'CBZManga':
        if os.path.exists(uri) and os.path.isdir(uri):
            info = CBZManga.load_info_file(CBZManga.get_info_file_path(uri))
            
            info_keys = info.keys()
            
            authors = info['authors'] if 'authors' in info_keys else []
            alternatives = info['alternatives'] if 'alternatives' in info_keys else []
            m_status = info['status'] if 'status' in info_keys else status.UNKNOWN
            name = info['name'] is 'name' if 'name' in info_keys else os.path.basename(uri)
            
            return CBZManga(name, authors, alternatives, m_status, uri)
        
        return None

    def load_info_file(file: str) -> Dict[Any, Any]:
        if os.path.exists(file):
            return json.loads(open(file, 'rb').read())
        return {}

    def get_info(self) -> Dict[Any, Any]:
        return CBZManga.load_info_file(self.info_file_path())
    
