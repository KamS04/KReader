from typing import Generator, List

from ....classes import source

from . import manga

import tkinter as tk
import requests
import json

_tmp_uri = None

def _set_tmp_uri(root: tk.Tk, uri: str):
    global _tmp_uri
    _tmp_uri = uri
    root.destroy()

class MangaDex(source.Source):
    name = 'mangadex.org'
    _search_api = 'http://api.mangadex.org/manga?'

    def choose() -> str:
        global _tmp_uri
        _tmp_uri = None
        
        root = tk.Tk()
        sx = 400
        sy = 75
        px = int((root.winfo_screenwidth() // 2) - (sx // 2))
        py = int((root.winfo_screenheight() // 2) - (sy // 2))
        root.winfo_toplevel().title('MangaDex')
        root.wm_geometry('%dx%d+%d+%d' % (sx, sy, px, py))

        label = tk.Label(root, text='Enter url')
        label.pack()

        entry = tk.Entry(root, width=40)
        entry.pack()

        button = tk.Button(root, text='Find', command=lambda *args: _set_tmp_uri(root, entry.get()))

        button.pack()
        root.mainloop()

        return _tmp_uri
    
    def get(uri: str):
        if manga.MangaDexManga.match_query.match(uri):
            return manga.MangaDexManga.from_uri(uri)
        return None

    def call_search_for_manga(query, offset=0, limit=20):
        url = MangaDex._search_api + 'title=%s&offset=%d&limit=%d&contentRating[]=safe&contentRating[]=suggestive&contentRating[]=erotica&contentRating[]=pornographic' % (query, offset, limit)
        return requests.get(url)

    def get_search_data(query) -> Generator[List[dict], None, None]:
        offset = 0
        while True:
            req = MangaDex.call_search_for_manga(query, offset=offset)
            if req.status_code == 200:
                all_data = json.loads(req.content)
                yield all_data['results']

                offset = all_data['offset']  + all_data['limit']
                total = all_data['total']
                if offset >= total:
                    break
            if req.status_code == 204:
                yield []
                break

    def search(query: str) -> Generator[List['manga.Manga'], None, None]:
        for results in MangaDex.get_search_data(query):
            mangas_found = [ manga.MangaDexManga.from_data(manga_data) for manga_data in results ]
            yield mangas_found

