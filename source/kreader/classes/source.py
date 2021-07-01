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
    def fetch_details_from_uri(self, uri: str) -> 'models.Manga':
        '''Turn the uri from choose_uri into a Manga object'''
        pass

    @abstractmethod
    def initialize(self, manga: 'models.Manga') -> 'models.Manga':
        '''Any Additional actions that need to be taken before a manga is saved or displayed'''
        pass

    @abstractmethod
    def search(self, query: str, title = True, author = False, group = False) -> Generator[List['models.Manga'], None, None]:
        '''Search for a specific query and filter'''
        pass

    @abstractmethod    
    def manga_to_data(self, manga: 'models.Manga'):
        '''Turn the object into a a dictionary to be saved to persistent storage
            Note, chapter data should also be saved here
        '''
        pass

    @abstractmethod
    def manga_from_data(self, data: dict) -> 'models.Manga':
        '''Create a Manga object from saved data
            Note, chapters should also be initialized from this saved data
        '''
        pass

    @abstractmethod
    def get_cover_image(self, manga: 'models.Manga') -> Tuple[BytesIO, str]:
        '''Fetch the cover image and turn it into BytesIO'''
        pass

    @abstractmethod
    def fetch_chapters(self, manga: 'models.Manga') -> Generator[List['models.Chapter'], None, None]:
        '''Fetch a list of chapters associated with this Manga'''
        pass

    @abstractmethod
    def fetch_number_of_pages(self, chapter: 'models.Chapter') -> int:
        ''' Fetch the number of pages in this chapter
            needed to create enough widgets to display the pages
            Also save any data that will be needed to render these pages in
            the chapter object, (i.e. design your chapter object to be able to save
            this data)
        '''
        pass
    
    @abstractmethod
    def render_page(self, chapter: 'models.Chapter', page_number: int) -> Tuple[BytesIO, str]:
        '''Render the page'''
        pass

    def finish_rendering(self, chapter: 'models.Chapter'):
        '''In case any action needs to be taken after all the pages are rendered'''
        pass

    @abstractproperty
    def can_sign_in(self) -> bool:
        '''Does the Source support siging in and therefore some form of a user list'''
        return False

    @abstractproperty
    def needs_to_intercept_cloudflare(self) -> bool:
        '''Displays the bypass cloudflare button'''
        return False

    def get_cloudflare_client(self) -> CloudFlareInterceptor:
        return None

    def get_sign_in_info(self) -> Any:
        ''' Do whatever is required to get whatever data the source needs (e.g. username) to sign in'''
        pass

    def sign_in(self, data):
        '''Sign in using the data recieved in get_sign_in_info'''
        pass

    def re_sign_in(self) -> bool:
        '''Try to sign in using values from the configuration return if sign in was successful'''
        pass

    def sign_out(self, data):
        pass


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
