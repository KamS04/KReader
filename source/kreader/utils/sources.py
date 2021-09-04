from types import ModuleType
from typing import Dict, List, Type

from functools import partial

from .. import source_utils
from ..plugin_sys import Plugin, loader
from ..ui import handlers
from ..classes.source import Source

SOURCEMANAGER: 'SourceManager' = None

class SourceManager:
    _instance = None

    @property
    def instance() -> 'SourceManager':
        print('in instance method')
        if SourceManager._instance is None:
            SourceManager._instance = SourceManager()
        return SourceManager._instance

    def __init__(self):
        self.paths = source_utils.get_prefs().plugin_paths.copy()
        self.install_path = source_utils.get_install_directory()
        print(self.paths, self.install_path)
        self.sources: List[Source] = []
        self._modules: List[ModuleType] = []
        self._plugin_classes: List[Type[Plugin]] = []
        self._plugin_module_map: Dict[Type[Plugin], ModuleType] = []

    async def load_sources(self):
        plugins, plugins_classes, modules, plugin_module_map = await handlers.PROCESSING( partial(self._load_plugins_from_paths, self.paths) )
        print('received plugins from other thread')
        self.add_plugins(plugins, plugins_classes, modules, plugin_module_map)
    
    async def _load_plugins_from_paths(self, paths):
        plugin_classes, modules, plugin_module_map = loader.load_plugins(*paths, check_class=lambda cls: issubclass(cls, Source) )
        print('loaded plugins from files')
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

    def _update_unneccessary(self, modules: List[ModuleType], plugin_classes: List[Type[Plugin]], plugin_module_map: Dict[Type[Plugin], ModuleType]):
        for cls in plugin_classes:
            self._plugin_classes.append(cls)
        
        for module in modules:
            self._modules.append(module)
        
        for k, v in plugin_module_map.items():
            self._plugin_module_map[k] = v


def create_now():
    global SOURCEMANAGER
    if SOURCEMANAGER is None:
        SOURCEMANAGER = SourceManager()
    return SOURCEMANAGER
