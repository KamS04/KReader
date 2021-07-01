from typing import List, Generator, Any

from abc import abstractmethod, abstractproperty, ABCMeta
from ..plugin_sys import ConfigurablePlugin, Plugin
from ..config_sys import Configurable


class Source(metaclass=ABCMeta):
    @abstractmethod
    def choose_uri(self) -> str:
        '''Do whatever is required to choose a uri'''
        pass

    @abstractmethod
    def get_from_uri(self, uri: str) -> 'manga.Manga':
        '''Turn the uri from choose_uri into a Manga object'''
        pass

    @abstractmethod
    def search(self, query: str, title = True, author = False, group = False) -> Generator[List['manga.Manga'], None, None]:
        '''Search for a specific query and filter'''
        pass

    @abstractmethod
    def from_data(self, data: dict) -> 'manga.Manga':
        '''Create a Manga object from saved data'''
        pass

    @abstractproperty
    def can_sign_in(self) -> bool:
        '''Does the Source support siging in and therefore some form of a user list'''
        return False

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
