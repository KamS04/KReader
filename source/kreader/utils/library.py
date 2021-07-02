from typing import List, Tuple
import sqlite3
import os

from ..classes.system import *

# Mangas Table
MANGAS_TABLE = 'MangasTable'
MANGA_ID = 'MangaId'
MANGA_SOURCE = 'MangaSource'
MANGA_DATA = 'MangaData'

MANGA_TABLE_QUERY = f'''CREATE TABLE IF NOT EXISTS {MANGAS_TABLE} (
    {MANGA_ID} integer primary key,
    {MANGA_SOURCE} text,
    {MANGA_DATA} blob
);'''


# Chapters Table
CHAPTERS_TABLE = 'ChaptersTable' 
CHAPTER_ID = 'ChapterId'
CHAPTER_MANGA = 'AssociatedManga'
CHAPTER_DATA = 'ChapterData'
CHAPTER_READ = 'ChapterRead'

CHAPTER_TABLE_QUERY = f'''CREATE TABLE IF NOT EXISTS {CHAPTERS_TABLE} (
    {CHAPTER_ID} integer primary key,
    {CHAPTER_MANGA} integer,
    {CHAPTER_READ} integer,
    {CHAPTER_DATA} blob
);'''


class Library:
    _db: sqlite3.Connection = None

    def __init__(self, database_file):
        self.database_file = None
    
    @property
    def db(self) -> sqlite3.Connection:
        if self._db is None:
            self._db = sqlite3.connect(self.database_file)
            self._db.execute(MANGA_TABLE_QUERY)
            self._db.execute(CHAPTER_TABLE_QUERY)
            self._db.commit()
        return self._db

    # Manga

    def _insert_manga(self, raw_manga_bundle: RawMangaBundle, db=None) -> int:
        cursor = (self.db if db is None else db).execute(
            f'INSERT INTO {MANGAS_TABLE} ({MANGA_SOURCE}, {MANGA_DATA}) VALUES(?, ?);',
            (raw_manga_bundle.source_key, raw_manga_bundle.manga_data,)
        )
        return cursor.lastrowid

    def add_manga_to_library(self, raw_manga_bundle: RawMangaBundle, *raw_chapter_bundles: RawChapterBundle) -> Tuple[RawMangaBundle, List[RawChapterBundle]]:
        with self.db as db:
            manga_id = self._insert_manga(raw_manga_bundle, db)
            final_manga_bundle = RawMangaBundle(
                manga_id,
                raw_manga_bundle.source_key,
                raw_manga_bundle.manga_data
            )

            final_chapter_bundles = self._insert_chapters(manga_id, raw_chapter_bundles, db)
                
        return final_manga_bundle, final_chapter_bundles

    def get_manga_data(self, id) -> RawMangaBundle:
        cursor = self.db.execute(f'SELECT * FROM {MANGAS_TABLE} WHERE {MANGA_ID} = ?', (id,))
        return RawMangaBundle(cursor.fetchone())

    def get_mangas_data(self) -> List[RawMangaBundle]:
        cursor = self.db.execute(f'SELECT * FROM {MANGAS_TABLE}')
        return [ RawMangaBundle(row) for row in cursor.fetchall() ]

    def update_manga(self, raw_manga_bundle: RawMangaBundle) -> int:
        with self.db as db:
            cursor = db.execute(
                f'UPDATE {MANGAS_TABLE} SET {MANGA_SOURCE} = ?, {MANGA_DATA} = ? WHERE {MANGA_ID} = ?;',
                (raw_manga_bundle.source_key, raw_manga_bundle.manga_data, raw_manga_bundle.manga_id,)
            )
        return cursor.lastrowid

    def remove_manga_from_library(self, raw_manga_bundle: RawMangaBundle):
        with self.db as db:
            db.execute(
                f'DELETE FROM {MANGAS_TABLE} WHERE {MANGA_ID} = ?',
                (raw_manga_bundle.manga_id,)
            )
            self._delete_chapters(raw_manga_bundle.manga_id, db)

    # Chapter

    def _insert_chapters(self, manga_id, raw_chapter_bundles: Tuple[RawChapterBundle], db=None) -> List[RawChapterBundle]:
        db = self.db if db is None else db
        final_chapter_bundles: List[RawChapterBundle] = []

        for chapter_bundle in raw_chapter_bundles:
            cursor = db.execute(
                f'INSERT INTO {CHAPTERS_TABLE} ({CHAPTER_MANGA}, {CHAPTER_READ}, {CHAPTER_DATA}) VALUES(?, ?, ?);',
                (manga_id, chapter_bundle.read, chapter_bundle.chapter_data)
            )
            final_chapter_bundles.append(RawChapterBundle(
                cursor.lastrowid,
                manga_id,
                chapter_bundle.read,
                chapter_bundle.chapter_data
            ))
        
        return final_chapter_bundles

    def get_chapters_data(self) -> List[RawChapterBundle]:
        cursor = self.db.execute(f'SELECT * FROM {CHAPTERS_TABLE}')
        return [ RawChapterBundle(row) for row in cursor.fetchall() ]

    def get_chapter_data(self, id) -> RawChapterBundle:
        cursor = self.db.execute(f'SELECT * FROM {CHAPTERS_TABLE} WHERE {CHAPTER_ID} = ?', (id,))
        return RawChapterBundle(cursor.fetchone())

    def get_associated_chapters(self, manga_id) -> List[RawChapterBundle]:
        cursor = self.db.execute(f'SELECT * FROM {CHAPTERS_TABLE} WHERE {CHAPTER_MANGA} = ?', (manga_id,))
        return [ RawChapterBundle(row) for row in cursor.fetchall() ]

    def update_chapters(self, raw_manga_bundle: RawMangaBundle, *raw_chapter_bundles: RawChapterBundle) -> List[RawChapterBundle]:
        with self.db as db:
            self._delete_chapters(raw_manga_bundle.manga_id, db)
            final_chapter_bundles = self._insert_chapters(raw_manga_bundle.manga_id, raw_chapter_bundles, db)
        return final_chapter_bundles

    def _delete_chapters(self, manga_id, db=None):
        (self.db if db is None else db).execute(f'DELETE FROM {CHAPTERS_TABLE} WHERE {CHAPTER_MANGA} = ?;', (manga_id,))

    # Misc

    def commit(self):
        self.db.commit()
    
    def close(self):
        self.commit()
        self.db.close()
        self._db = None