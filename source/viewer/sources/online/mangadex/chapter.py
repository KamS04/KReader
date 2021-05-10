from typing import List, Dict, Any

import sys
import re
import requests
import json

from ....classes import chapter
from . import manga, page
from .maps import LANGUAGE_MAP

#             <    http   ><      website                  ><        api              ><                               uuid                                           >< extra bits (normally title) >                        
url_regex = r'(http(s?)://)?(((www\.)?mangadex.org/chapter/)|api.mangadex.org/chapter/)[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}(/.*|/)?'
uuid_regex = r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'


class MangaDexChapter(chapter.Chapter):
    match_query = re.compile(url_regex)
    _uuid_query = re.compile(uuid_regex)
    _chapter_api = 'http://api.mangadex.org/chapter/%s'
    _required_meta_keys = {
        'title',
        'groups',
        'chapter_language',
        'hash',
        'language'
    }
    _chapter_uri = 'http://mangadex.org/chapter/%s'
    _server_api = 'http://api.mangadex/at-home/server/%s'
    _groups_api_endpoint = 'http://api.mangadex.org/group?'

    def call_chapter_api(uuid: str) -> requests.Response:
        return requests.get(MangaDexChapter._chapter_api % uuid)

    def get_uuid_from_uri(uri: str):
        return MangaDexChapter._uuid_query.findall(uri)[0]

    def get_groups(*group_uuids: str) -> List[str]:
        query_params = '&'.join( 'ids=[]' + uuid for uuid in group_uuids )
        url = MangaDexChapter._authors_api_endpoint + query_params + '&limit=%d' % len(group_uuids) # I'm assuming there's going to be less than 100 groups
        req = requests.get(url)
        
        if req.status_code == 200:
            data = json.loads(req.content)
            groups = [ info['data']['attributes']['name'] for info in data['results'] ]
            return groups
            
        return []

    def __init__(self, manga: 'manga.MangaDexManga', title: str, groups: List[str], chapter_num: float, language: str, uri: str, chapter_hash: str, page_files: List[str], chapter_uuid: str=None):
        super().__init__(manga, title, groups, chapter_num, language, uri)
        self.chapter_hash = chapter_hash
        self.chapter_uuid = chapter_uuid if chapter_uuid else MangaDexChapter.get_uuid_from_uri(self.uri)
        self.page_files = page_files

    def get_data_server(self) -> str:
        url = self._server_api % self.chapter_uuid
        req = requests.get(url)
        return json.loads(req.content)['baseUrl'] # I'm assuming this will work, but if you try to send more than 60 of these in a minute the app will crash

    def get_pages(self) -> List['page.MangaDexPage']:
        server = self.get_data_server()
        pages: List[page.MangaDexPage] = []
        for idx, page_file in enumerate(self.page_files):
            page_found = page.MangaDexPage(idx + 1, self, None, server, page_file)
            pages.append(page_found)
        
        return pages

    def from_data(manga: 'manga.MangaDexManga', data: dict) -> 'MangaDexChapter':
        title = data['data']['attributes']['title']
        
        uuid = data['data']['id']

        group_uuids = { rel['id'] for rel in data['relationships'] if rel['type'] == 'scanlation_group' }
        groups = MangaDexChapter.get_groups(*group_uuids)

        chapter_str: str = data['data']['attributes']['chapter']
        integer, point, float_bits = chapter_str.partition('.')
        chapter_num = float( integer + point + float_bits.replace('.', '') ) # This is highly unecessary for most people but "Tedama ni Toritai Kurokiya-san" has a chapter where the number is 1.5.1

        language = LANGUAGE_MAP[ data['data']['attributes']['translatedLanguage'] ]

        uri = MangaDexChapter._chapter_uri % uuid

        chapter_hash = data['data']['attributes']['hash']

        pages = data['data']['attributes']['data'] # I'm using the regular images, if you want to use datasaver change the last ['data'] to ['dataSaver']

        return MangaDexChapter(manga, title, groups, chapter_num, language, uri, chapter_hash, pages, uuid)

    def from_uri(uri: str, manga: 'manga.Manga', metadata: Dict[Any, Any]) -> 'MangaDexChapter':
        uuid = MangaDexChapter.get_uuid_from_uri(uri)
        req = MangaDexChapter.call_chapter_api(uuid)
        if req.status_code == 200:
            return MangaDexChapter.from_data(manga, json.loads(req.content))
        
        return None

