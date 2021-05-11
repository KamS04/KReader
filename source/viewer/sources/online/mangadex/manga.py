from typing import List, Pattern, Tuple, Generator

import re
from io import BytesIO
import requests
import json
import os

from ....classes import manga
from . import chapter
from .maps import LANGUAGE_MAP, STATUS_MAP

#             <    http   ><      website      ><website endpoint><        api           ><                               uuid                                           >< extra bits (normally title) >                        
url_regex = r'(http(s?)://)?(((www\.)?mangadex.org/(manga|title)/)|api.mangadex.org/manga/)[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}(/.*|/)?'
uuid_regex = r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'

class MangaDexManga(manga.Manga):
    match_query: Pattern = re.compile(url_regex)
    uuid_query: Pattern = re.compile(uuid_regex)
    _base_api = 'https://api.mangadex.org/'
    _manga_api = _base_api + 'manga/%s'
    _chapter_for_manga_api = _base_api + 'chapter?manga=%s&limit=%d&offset=%d'
    _chapter_api = _base_api + 'chapter/%s'
    _authors_api_endpoint = _base_api + 'author?'

    def call_manga_api(uuid: str) -> requests.Response:
        return requests.get(MangaDexManga._manga_api % uuid)
    
    def call_get_chapters_list(self, manga_uuid, limit=20, offset=0) -> requests.Response:
        return requests.get(MangaDexManga._chapter_for_manga_api % (manga_uuid, limit, offset))

    def call_chapter_api(self, chapter_uuid: str):
        return requests.get(MangaDexManga._chapter_api % chapter_uuid)

    def get_uuid_from_uri(uri: str) -> str:
        return MangaDexManga.uuid_query.findall(uri)[0]
    
    def get_authors(*author_uuids: str) -> List[str]:
        query_params = '&'.join( 'ids=[]' + uuid for uuid in author_uuids )
        url = MangaDexManga._authors_api_endpoint + query_params + '&limit=%d' % len(author_uuids) # I'm assuming there's going to be less than 100 authors
        req = requests.get(url)
        
        if req.status_code == 200:
            data = json.loads(req.content)
            authors = [ info['data']['attributes']['name'] for info in data['results'] ]

            return authors
        return []

    def gen_chapters_json(self) -> Generator[List[dict], None, None]:
        offset = 0
        while True:
            req = self.call_get_chapters_list(self.uuid, offset=offset)
            if req.status_code == 200:
                all_data = json.loads(req.content)
                yield all_data['results']

                offset = all_data['offset'] + all_data['limit']
                total = all_data['total']
                if offset >= total:
                    break


    def __init__(self, title: str, authors: List[str], alt_titles: List[str], status: int, uri: str, manga_uuid: int = None):
        super().__init__(title, authors, alt_titles, status, uri)
        self.uuid = manga_uuid if manga_uuid else MangaDexManga.get_uuid_from_uri(self.uri)
    
    def get_chapters(self) -> List['chapter.MangaDexChapter']:
        for results in self.gen_chapters_json():
            yield [chapter.MangaDexChapter.from_data(self, chapter_info) for chapter_info in results]

    def get_cover_image(self) -> Tuple[BytesIO, str]:
        # Mangadex API doesn't support cover images yet
        return None
    
    def from_data(data: dict, uri: str=None, uuid: str=None) -> 'MangaDexManga':   
        if uuid is None:
            uuid = data['data']['id']
        if uri is None:
            uri = MangaDexManga._manga_api % uuid

        alt_titles = [ title['en'] for title in data['data']['attributes']['altTitles'] if 'en' in title.keys()]
        status = STATUS_MAP[ data['data']['attributes']['status'] ]
        title = data['data']['attributes']['title']['en']

        # this is a set because sometimes the author and artist is the same but is listed twice, but I don't want duplicate uuids
        author_uuids = { rel['id'] for rel in data['relationships'] if rel['type'] == 'author' or rel['type'] == 'artist' }
        authors = MangaDexManga.get_authors(*author_uuids)

        return MangaDexManga(title, authors, alt_titles, status, uri, uuid)

    def from_uri(uri: str) -> 'MangaDexManga':
        if MangaDexManga.match_query.match(uri):
            uuid = MangaDexManga.get_uuid_from_uri(uri)
            req = MangaDexManga.call_manga_api(uuid)

            if req.status_code == 200:
                data = json.loads(req.content)
                return MangaDexManga.from_data(data, uri, uuid)
            
        return None