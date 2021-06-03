from abc import ABCMeta, abstractproperty, abstractmethod
from ..source_sdk.config import Configurable


class Plugin(metaclass=ABCMeta):
    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def can_sign_in(self):
        pass

    @abstractmethod
    def request_configurable(self):
        return None, None
    
    def upgrade_configuration(self, previous_config, config_version):
        return None
    
    @property
    def configuration(self) -> Configurable:
        return None
    
    @configuration.setter
    def configuration(self, configuration):
        pass
    
    def get_editable_configuration(self):
        if self.configuration is not None:
            return self.configuration.copy()
        return None
    
    @abstractmethod
    def execute(self):
        pass
    
    def __str__(self):
        return self.name

