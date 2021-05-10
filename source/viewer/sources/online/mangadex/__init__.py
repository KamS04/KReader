from ....classes import source

from . import manga

import tkinter as tk

_tmp_uri = None

def _set_tmp_uri(root: tk.Tk, uri: str):
    global _tmp_uri
    _tmp_uri = uri
    root.destroy()

class MangaDex(source.Source):
    name = 'mangadex.org'

    def choose() -> str:
        global _tmp_uri
        _tmp_uri = None
        
        root = tk.Tk()
        sx = 400
        sy = 75
        px = int((root.winfo_screenwidth() // 2) - (sx // 2))
        py = int((root.winfo_screenheight() // 2) - (sy // 2))
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
