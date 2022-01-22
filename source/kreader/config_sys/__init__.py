import json
from .properties import Property

def create_config(version):
    def _create_config(cls):
        for prop_name in vars(cls):
            prop = cls.__getattribute__(cls, prop_name)
            if isinstance(prop, Property):
                cls._props_map[prop_name] = prop
        
        for prop_name in cls._props_map.keys():
            delattr(cls, prop_name)
        
        cls._version = version

        return cls
    
    return _create_config


class OutdatedConfigurableException(ValueError):
    def __init__(self, name, version):
        super(OutdatedConfigurableException, self).__init__(OutdatedConfigurableException._get_message(name, version))
        self.name = name
        self.version = version
    
    @staticmethod
    def _get_message(name, version):
        return f'Configurable version {version} for plugin {name} is outdated and cannot be upgraded'
    
    @property
    def message(self):
        return OutdatedConfigurableException._get_message(self.name, self.version)


class Configurable(object):
    _props_map = {}
    _write_callback = None

    def __init__(self, **kwargs):
        props_map = {}
        for prop_name, prop in self._props_map.items():
            prop_type = type(prop)
            if prop_name in kwargs.keys():
                data = kwargs[prop_name]
            else:
                data = prop.to_dict()

            n_prop = prop_type(**data)
            props_map[prop_name] = n_prop
        
        self._props_map = props_map
    
    def __getattr__(self, name):
        if name in self.__getattribute__('_props_map').keys():
            return self.__getattribute__('_props_map')[name].get_value()
        raise AttributeError(name)
    
    def __setattr__(self, name, value):
        if name in self._props_map.keys():
            self._props_map[name].set_value(value)
            if self._write_callback is not None:
                self._write_callback(self)
        else:
            super(Configurable, self).__setattr__(name, value)
    
    @property
    def data(self):
        return { key: prop.to_dict() for key, prop in self._props_map.items() }
    
    def json(self):
        return json.dumps(self.data)
    
    def copy(self):
        return type(self)(**self.data)

