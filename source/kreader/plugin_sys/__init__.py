from abc import ABCMeta, abstractproperty, abstractmethod
from ..config_sys import Configurable


class Plugin(metaclass=ABCMeta):
    _unique_key: str = None
    '''Plugin base class that defines fucntions required by the loader
        Let your plugin derive from this and extend it to include the functions you need
    '''
    @abstractproperty
    def name(self):
        '''Name of the plugin used to identify the plugin's save data'''
        pass
    
    def __str__(self):
        return self.name


class ConfigurablePlugin(Plugin):
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
    
    @abstractmethod
    def request_configurable(self):
        '''Return the configurable class as well as its version'''
        return None, None
    
    def upgrade_configuration(self, previous_config, config_version):
        '''The configuration found in the prefs file was outdated, try to update it'''
        return None
    
    def get_editable_configuration(self):
        '''Used to edit the configurable so that no changes are applied before the the setter is called'''
        if self.configuration is not None:
            return self.configuration.copy()
        return None