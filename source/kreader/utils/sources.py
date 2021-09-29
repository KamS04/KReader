import asyncio
from types import ModuleType
from typing import Dict, List, Type

from functools import partial

from .. import source_utils
from ..plugin_sys import Plugin, loader, installer
from ..ui import handlers
from ..thread_sys import run_in_handler
from ..classes.source import Source

from pubsub import pub

SOURCEMANAGER: 'SourceManager' = None

SOURCE_UPDATE_TOPIC = 'SOURCE_UPDATE'

class SourceManager:
    def __init__(self):
        self.paths = set(source_utils.get_prefs().plugin_paths)
        self.install_path = source_utils.get_install_directory()
        self.sources: List[Source] = []
        self._modules: List[ModuleType] = []
        self._plugin_classes: List[Type[Plugin]] = []
        self._plugin_module_map: Dict[Type[Plugin], ModuleType] = {}

        def _write_config_change(unique_key, configuration):
            async def _async_write_config_change():
                prefs = source_utils.get_prefs()
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
        plugin_classes, modules, plugin_module_map = loader.load_plugins(*paths, check_class=lambda cls: issubclass(cls, Source) )
        plugins = loader.initialize_plugins(
            plugin_classes, 
            plugin_module_map, 
            source_utils.get_prefs().plugin_data
        )
        return plugins, plugin_classes, modules, plugin_module_map
    
    def add_plugins(self, plugins: List[Source], modules: List[ModuleType], plugin_classes: List[Type[Plugin]], plugin_module_map: Dict[Type[Plugin], ModuleType]):
        self._update_unneccessary(modules, plugin_classes, plugin_module_map)
        
        for plugin in plugins:
            self.sources.append(plugin)
        pub.sendMessage(SOURCE_UPDATE_TOPIC)

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
        prefs = source_utils.get_prefs()
        prefs.edit.plugin_paths = list(self.paths)
        prefs.dump_changes()


def create_now():
    global SOURCEMANAGER
    if SOURCEMANAGER is None:
        SOURCEMANAGER = SourceManager()
    return SOURCEMANAGER
