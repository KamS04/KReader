from typing import List, Generator, Any, Tuple

from abc import abstractmethod, abstractproperty, ABCMeta
from io import BytesIO

from ..utils.cloudflare import CloudFlareInterceptor
from ..plugin_sys import ConfigurablePlugin, Plugin
from ..config_sys import Configurable

from . import models

class Source(metaclass=ABCMeta):
    @abstractmethod
    def choose_uri(self) -> str:
        '''Do whatever is required to choose a uri'''
        pass

    @abstractmethod
    async def fetch_details_from_uri(self, uri: str) -> 'models.Manga':
        '''Turn the uri from choose_uri into a Manga object'''
        pass

    @abstractmethod
    async def initialize(self, manga: 'models.Manga') -> 'models.Manga':
        '''Any Additional actions that need to be taken before a manga is saved or displayed'''
        pass

    @abstractmethod
    async def search(self, query: str, title = True, author = False, group = False) -> Generator[List['models.Manga'], None, None]:
        '''Search for a specific query and filter'''
        pass

    @abstractmethod    
    def manga_to_data(self, manga: 'models.Manga') -> dict:
        '''Turn the object into a a dictionary to be saved to persistent storage
            Note, chapter data should also be saved here
        '''
        pass

    @abstractmethod
    def manga_from_data(self, data: dict) -> 'models.Manga':
        '''Create a Manga object from saved data
        '''
        pass

    @abstractmethod
    async def get_cover_image(self, manga: 'models.Manga') -> Tuple[BytesIO, str]:
        '''Fetch the cover image and turn it into BytesIO'''
        pass

    @abstractmethod
    async def fetch_chapters(self, manga: 'models.Manga') -> Generator[List['models.Chapter'], None, None]:
        '''Fetch a list of chapters associated with this Manga'''
        pass

    @abstractmethod
    def chapters_to_data(self, chapter: 'models.Chapter') -> dict:
        '''Turn chapter to data that can be saved'''
        pass

    @abstractmethod
    async def fetch_number_of_pages(self, chapter: 'models.Chapter') -> int:
        ''' Fetch the number of pages in this chapter
            needed to create enough widgets to display the pages
            Also save any data that will be needed to render these pages in
            the chapter object, (i.e. design your chapter object to be able to save
            this data)
        '''
        pass
    
    @abstractmethod
    async def render_page(self, chapter: 'models.Chapter', page_number: int) -> Tuple[BytesIO, str]:
        '''Render the page'''
        pass

    async def finish_rendering(self, chapter: 'models.Chapter'):
        '''In case any action needs to be taken after all the pages are rendered'''
        pass

    @abstractproperty
    def can_sign_in(self) -> bool:
        '''Does the Source support siging in and therefore some form of a user list'''
        return False

class StaticSource(Plugin, Source):
    def __str__(self):
        return self.name

class ConfigurableSource(ConfigurablePlugin, Source):
    '''Plugin base class that assumes a configurable will exist
        and sets up the required private and public properties
        DOES NOT DO ANY FORM OF CONFIGURATION VALIDATION
    '''    
    _configurable = None
    
    @property
    def configuration(self) -> Configurable:
        return self._configurable
    
    @configuration.setter
    def configuration(self, configuration) -> Configurable:
        self._configuration = configuration
    
    def __str__(self):
        return self.name

class SourceWithAccounts(ConfigurableSource):
    def get_sign_in_info(self) -> Any:
        ''' Do whatever is required to get whatever data the source needs (e.g. username) to sign in'''
        pass

    async def sign_in(self, data):
        '''Sign in using the data recieved in get_sign_in_info'''
        pass

    async def re_sign_in(self) -> bool:
        '''Try to sign in using values from the configuration return if sign in was successful'''
        pass

    async def sign_out(self, data):
        pass

class CloudFlareBlockedSource(ConfigurableSource):
    _client = None
    
    @abstractproperty
    def domain(self) -> str:
        """The domain that the source will pull data from"""
        return ''

    @property
    def cloudflare_client(self) -> CloudFlareInterceptor:
        if self._client is None:
            self._client = CloudFlareInterceptor(self.domain)
        return self._client
