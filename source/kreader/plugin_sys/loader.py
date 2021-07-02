from typing import List

import os
import pkgutil

from . import Plugin
from .. import source_utils
from ..config_sys import Configurable, OutdatedConfigurableException

def create_plugin_key(plugin, module):
    return module.__path__[0] + ' # ' + plugin.name

def map_plugin_key(plugin, modules_map):
    return create_plugin_key(plugin, modules_map[plugin])

def load_plugins(*pacakge_paths, debug=True):
    plugins: List[Plugin] = []

    def _register(plugin): # Append a plugin into the accumulating list of plugins
        if debug:
            print('registering', plugin)
        plugins.append(plugin)
    
    old_register = source_utils.register
    source_utils.register = _register # now any module using the register function will use the custom register function

    parent_dirs = {}
    for package_path in pacakge_paths:
        parent_dir = os.path.dirname(package_path)

        if parent_dir in parent_dirs.keys():
            parent_dirs[parent_dir].append(os.path.basename(package_path))
        else:
            parent_dirs[parent_dir] = [ os.path.basename(package_path) ]

    modules = []
    for package in pkgutil.iter_modules(list(parent_dirs.keys())):
        finder, name, is_pkg = package
        if name in parent_dirs[finder.path]:
            spec = finder.find_spec(name)
            module = spec.loader.load_module(name)
            modules.append(module)
        
    source_utils.register = old_register # reset the register function so no new plugins can be registered

    modules_map = { module.__name__: module for module in modules }
    plugin_module_map = { plugin: modules_map[plugin.__module__] for plugin in plugins }

    return plugins, modules, plugin_module_map

def initialize_plugins(plugin_classes: List[Plugin], modules_map, plugin_data: dict):
    plugins: List[Plugin] = []

    for plugin_cls in plugin_classes:
        plugin: Plugin = plugin_cls() # Therefore plugins must not have any __init__ parameters
        #instead set up any of these parameters in a configuration object

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
    configurable, version = plugin.request_configurable()

    if configurable is None:
        return None, None
    
    configuration = plugin.configuration
    config = configuration.data
    data = { 'version': version, 'config': config }
    plugin_key = plugin._unique_key
    return plugin_key, data