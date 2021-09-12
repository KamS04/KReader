from types import ModuleType
from typing import Dict, List, Tuple, Type

import os
import pkgutil

from . import ConfigurablePlugin, Plugin
from .. import source_utils
from ..config_sys import Configurable, OutdatedConfigurableException

def create_plugin_key(plugin, module):
    return module.__path__[0] + ' # ' + plugin.name

def map_plugin_key(plugin, modules_map):
    return create_plugin_key(plugin, modules_map[plugin])

def load_plugins(*pacakge_paths, debug=True, check_class= None) -> Tuple[ List[Type[Plugin]], List[ModuleType], Dict[ Type[Plugin], ModuleType]]:
    plugin_classes: List[Type[Plugin]] = []

    def _register(plugin_cls): # Append a plugin into the accumulating list of plugins
        if debug:
            print('registering', plugin_cls)
        if check_class is not None and not check_class(plugin_cls):
            raise ValueError(f'{plugin_cls} is not of the right class')
        plugin_classes.append(plugin_cls)
    
    old_register = source_utils.register
    source_utils.register = _register # now any module using the register function will use the custom register function

    parent_dirs = {}
    for package_path in pacakge_paths:
        parent_dir = os.path.dirname(package_path)

        if parent_dir in parent_dirs.keys():
            parent_dirs[parent_dir].append(os.path.basename(package_path))
        else:
            parent_dirs[parent_dir] = [ os.path.basename(package_path) ]

    modules: List[ModuleType] = []
    for package in pkgutil.iter_modules(list(parent_dirs.keys())):
        finder, name, is_pkg = package
        if name in parent_dirs[finder.path]:
            spec = finder.find_spec(name)
            try:
                module = spec.loader.load_module(name)
                modules.append(module)
            except ValueError as exc:
                if debug:
                    print(exc)

    source_utils.register = old_register # reset the register function so no new plugins can be registered

    modules_map = { module.__name__: module for module in modules }
    plugin_module_map: Dict[Type[Plugin], ModuleType] = { plugin_cls: modules_map[plugin_cls.__module__] for plugin_cls in plugin_classes }

    return plugin_classes, modules, plugin_module_map

def initialize_plugins(plugin_classes: List[Plugin], modules_map, plugin_data: dict) -> List[Plugin]:
    plugins: List[Plugin] = []

    for plugin_cls in plugin_classes:
        plugin: Plugin = plugin_cls() # Therefore plugins must not have any __init__ parameters
        #instead set up any of these parameters in a configuration object

        if isinstance(plugin, ConfigurablePlugin):
            configurable: Configurable = None
            configurable, version = plugin.request_configurable()

            if configurable is not None:
                configuration = None
                plugin_key = map_plugin_key(plugin_cls, modules_map)

                config_keys = {}
                if plugin_key in plugin_data.keys():
                    pre_data = plugin_data[plugin_key]
                    pre_version = pre_data['version']
                    pre_config = pre_data['config']

                    if pre_version < version:
                        try:
                            pre_config = plugin.upgrade_configuration(pre_config, pre_version)
                            if pre_config is None:
                                pre_config = {}
                        except OutdatedConfigurableException as e:
                            print('Outdated configuration for ', plugin.name)
                    elif pre_version > version:
                        print('Configuration for', plugin.name, 'is newer than the plugin')
                        pre_config = {}
                    
                    config_keys = pre_config
                
                configuration = configurable(**config_keys)

                plugin.configuration = configuration
        
        plugin._unique_key = plugin_key

        plugins.append(plugin)
    
    return plugins

def convert_to_data(plugin: Plugin):
    if isinstance(plugin, ConfigurablePlugin):
        configurable, version = plugin.request_configurable()

        if configurable is None:
            return None
        
        configuration = plugin.configuration
        config = configuration.data
        data = { 'version': version, 'config': config }
        plugin_key = plugin._unique_key
        return plugin_key, data
    return None