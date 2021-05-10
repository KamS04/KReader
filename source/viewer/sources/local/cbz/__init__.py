from ....classes.source import Source

from .manga import CBZManga

import os
from tkinter import Tk
from tkinter import filedialog

def verify(path: str) -> bool:
    ''' Makes sure the selected path is not None, exists, and is a directory '''
    return (path and 
            os.path.exists(path) and
            os.path.isdir(path))


class CBZ(Source):
    name = 'CBZ'

    def choose() -> str:
        ''' Creates a filedialog to find a directory which '''
        root = Tk()
        root.withdraw()
        path = filedialog.askdirectory()
        root.destroy()

        return path if verify(path) else None

    def get(uri: str) -> CBZManga:
        return CBZManga.from_uri(uri) if verify(uri) else None

