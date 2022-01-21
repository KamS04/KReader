import os
import asyncio
from types import ModuleType
from typing import Dict, List, Type

from functools import partial

from .. import source_utils
from ..plugin_sys import Plugin, loader, installer
from ..ui import handlers
from ..classes.source import Source

from . import publisher

SOURCEMANAGER: 'SourceManager' = None

SOURCE_UPDATE_TOPIC = 'SOURCE_UPDATE'

class SourceManager:
    def __init__(self):
        with source_utils.get_prefs() as prefs:
            self.paths = set(prefs.plugin_paths)
        self.install_path = source_utils.get_install_directory()
        self.sources: List[Source] = []
        self._modules: List[ModuleType] = []
        self._plugin_classes: List[Type[Plugin]] = []
        self._plugin_module_map: Dict[Type[Plugin], ModuleType] = {}

        def _write_config_change(unique_key, configuration):
            async def _async_write_config_change():
                with source_utils.get_prefs() as prefs:
                    data = loader.convert_configurartion_to_data(configuration)
                    prefs.plugin_data[unique_key] = data
                    prefs.dump_changes()
            asyncio.create_task( handlers.PROCESSING(_async_write_config_change) )
        
        source_utils.configuration_changed = _write_config_change

    async def load_sources(self):
        await self.load_sources_from_paths(*self.paths)
    
    async def load_sources_from_paths(self, *paths):
        plugins, plugins_classes, modules, plugin_module_map = await handlers.PROCESSING( partial(self._load_plugins_from_paths, *paths) )
        print('received %d plugins from other thread' % len(plugins))
        self.add_plugins(plugins, plugins_classes, modules, plugin_module_map)

    async def _load_plugins_from_paths(self, *paths):
        old_register = source_utils.register
        def reset_registerer():
            source_utils.register = old_register
        
        def set_registerer(registerer):
            source_utils.register = registerer

        plugin_classes, modules, plugin_module_map = loader.load_plugins(paths, set_registerer, reset_registerer=reset_registerer, check_class=lambda cls: issubclass(cls, Source) )
        with source_utils.get_prefs() as prefs:
            plugins = loader.initialize_plugins(
                plugin_classes, 
                plugin_module_map, 
                prefs.plugin_data
            )
        return plugins, plugin_classes, modules, plugin_module_map
    
    def add_plugins(self, plugins: List[Source], modules: List[ModuleType], plugin_classes: List[Type[Plugin]], plugin_module_map: Dict[Type[Plugin], ModuleType]):
        self._update_unneccessary(modules, plugin_classes, plugin_module_map)
        
        for plugin in plugins:
            self.sources.append(plugin)
        publisher.publish(SOURCE_UPDATE_TOPIC)

    def _update_unneccessary(self, modules: List[ModuleType], plugin_classes: List[Type[Plugin]], plugin_module_map: Dict[Type[Plugin], ModuleType]):
        for cls in plugin_classes:
            self._plugin_classes.append(cls)
        
        for module in modules:
            self._modules.append(module)
        
        for k, v in plugin_module_map.items():
            self._plugin_module_map[k] = v
    
    async def install_from_zip(self, zip_path):
        await handlers.PROCESSING(partial(self._install_from_zip, zip_path))

    async def _install_from_zip(self, zip_path):
        module_name, package_path = installer.install_plugin(self.install_path, zip_path)
        self._append_paths(package_path)
        await self.load_sources_from_paths(package_path)
    
    def _append_paths(self, *new_paths):
        old_length = len(self.paths)
        for path in new_paths:
            self.paths.add(path)
        if len(self.paths) != old_length:
            self._update_paths()

    def _update_paths(self):
        with source_utils.get_prefs() as prefs:
            prefs.edit.plugin_paths = list(self.paths)
            prefs.dump_changes()
    
    def resolve_asset_path(self, plugin, path):
        return self.resolve_asset_path_from_type(type(plugin), path)

    def resolve_asset_path_from_type(self, plugin_cls, path):
        if os.path.isabs(path):
            return path
        base_dir = os.path.dirname(self._plugin_module_map[plugin_cls].__file__)
        return os.path.abspath(base_dir + '/' + path)
    
    def uninstall_source(self, source):
        print('Uninstalling', source.name)


def create_now():
    global SOURCEMANAGER
    if SOURCEMANAGER is None:
        SOURCEMANAGER = SourceManager()
    return SOURCEMANAGER
