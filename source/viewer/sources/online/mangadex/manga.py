from typing import List, Pattern, Tuple, Generator

import re
from io import BytesIO
import requests
import json
import os
import html

from ....classes import manga
from . import chapter
from .maps import LANGUAGE_MAP, STATUS_MAP

#             <    http   ><      website      ><website endpoint><        api           ><                               uuid                                           >< extra bits (normally title) >                        
url_regex = r'(http(s?)://)?(((www\.)?mangadex.org/(manga|title)/)|api.mangadex.org/manga/)[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}(/.*|/)?'
uuid_regex = r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'

NO_IMAGES_FILE = os.path.join( os.path.dirname(__file__), 'cover.png' )
EXT = 'png'

_COVER = None

def load_cover_image() -> Tuple[BytesIO, str]:
    global _COVER
    if _COVER is None:
        file = open(NO_IMAGES_FILE, 'rb')
        _COVER = BytesIO(file.read())
    return _COVER, EXT



class MangaDexManga(manga.Manga):
    match_query: Pattern = re.compile(url_regex)
    uuid_query: Pattern = re.compile(uuid_regex)
    _base_api = 'https://api.mangadex.org/'
    _manga_api = _base_api + 'manga/%s'
    _chapter_for_manga_api = _base_api + 'chapter?manga=%s&limit=%d&offset=%d'
    _chapter_api = _base_api + 'chapter/%s'
    _authors_api_endpoint = _base_api + 'author?'
    _cover_art_api = _base_api + 'cover?manga=%s&order[createdAt]=desc'
    _cover_art_api_direct = _base_api + 'cover/%s'
    _cover_art_url = 'https://uploads.mangadex.org/covers/%s/%s.512.jpg'

    def call_manga_api(uuid: str) -> requests.Response:
        return requests.get(MangaDexManga._manga_api % uuid)
    
    def call_get_chapters_list(self, manga_uuid, limit=20, offset=0) -> requests.Response:
        return requests.get(MangaDexManga._chapter_for_manga_api % (manga_uuid, limit, offset))

    def call_chapter_api(self, chapter_uuid: str):
        return requests.get(MangaDexManga._chapter_api % chapter_uuid)

    def get_uuid_from_uri(uri: str) -> str:
        return MangaDexManga.uuid_query.findall(uri)[0]
    
    def get_authors(*author_uuids: str) -> List[str]:
        query_params = '&'.join( 'ids[]=' + uuid for uuid in author_uuids )
        url = MangaDexManga._authors_api_endpoint + query_params + '&limit=%d' % len(author_uuids) # I'm assuming there's going to be less than 100 authors
        req = requests.get(url)
        
        if req.status_code == 200:
            data = json.loads(req.content)
            authors = [ info['data']['attributes']['name'] for info in data['results'] ]

            return authors
        return []

    def get_cover_image_file_from_manga(uuid):
        req = requests.get(MangaDexManga._cover_art_api % uuid)

        if req.status_code == 200:
            data = json.loads(req.content)
            if data['total'] > 0:
                cover_art_id = data['results'][0]['data']['id']
                file_name = data['results'][0]['data']['attributes']['fileName']
                return cover_art_id, file_name
        return None, None

    def get_cover_image_file_from_uuid(uuid):
        req = requests.get(MangaDexManga._cover_art_api_direct % uuid)

        if req.status_code == 200:
            data = json.loads(req.content)
            if data['result'] == 'ok':
                return data['data']['attributes']['fileName']
        return None

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

    def __init__(self, title: str, authors: List[str], alt_titles: List[str], status: int, uri: str, manga_uuid: str = None, cover_art_uuid: str = None, cover_art_file_name: str = None):
        super().__init__(title, authors, alt_titles, status, uri)
        self.uuid = manga_uuid if manga_uuid else MangaDexManga.get_uuid_from_uri(self.uri)
        self._cover_art_uuid = cover_art_uuid
        self._cover_art_filename = cover_art_file_name
    
    def get_chapters(self) -> List['chapter.MangaDexChapter']:
        for results in self.gen_chapters_json():
            yield [chapter.MangaDexChapter.from_data(self, chapter_info) for chapter_info in results]

    def get_cover_art_filename(self):
        if self._cover_art_uuid is None:
            self._cover_art_uuid, self._cover_art_filename = MangaDexManga.get_cover_image_file_from_manga(self.uuid)
        else:
            self._cover_art_filename = MangaDexManga.get_cover_image_file_from_uuid(self._cover_art_uuid)

    def get_cover_image(self) -> Tuple[BytesIO, str]:
        if self._cover_art_filename is None:
            self.get_cover_art_filename()
        # Mangadex API doesn't support cover images yet
        if self._cover_art_filename is not None:
            url = MangaDexManga._cover_art_url % (self.uuid, self._cover_art_filename)
            req = requests.get(url)
            if req.ok:
                data = BytesIO(req.content)
                return data, 'jpg'
        return None
    
    def from_data(data: dict, uri: str=None, uuid: str=None) -> 'MangaDexManga':   
        if uuid is None:
            uuid = data['data']['id']
        if uri is None:
            uri = MangaDexManga._manga_api % uuid

        cover_art = [ relation for relation in data['relationships'] if relation['type'] == 'cover_art' ]
        cover_art = cover_art[0]['id'] if cover_art else None

        alt_titles = [ html.unescape( title['en'] ) for title in data['data']['attributes']['altTitles'] if 'en' in title.keys()]
        status = STATUS_MAP[ data['data']['attributes']['status'] ]
        title = html.unescape( data['data']['attributes']['title']['en'] )

        # this is a set because sometimes the author and artist is the same but is listed twice, but I don't want duplicate uuids
        author_uuids = { rel['id'] for rel in data['relationships'] if rel['type'] == 'author' or rel['type'] == 'artist' }
        authors = MangaDexManga.get_authors(*author_uuids)

        return MangaDexManga(title, authors, alt_titles, status, uri, uuid, cover_art)

    def from_uri(uri: str) -> 'MangaDexManga':
        if MangaDexManga.match_query.match(uri):
            uuid = MangaDexManga.get_uuid_from_uri(uri)
            req = MangaDexManga.call_manga_api(uuid)

            if req.status_code == 200:
                data = json.loads(req.content)
                return MangaDexManga.from_data(data, uri, uuid)
            
        return None