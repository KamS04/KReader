from typing import Any


class DefaultingDict(dict):
    def __init__(self, default: Any, map: dict):
        self.default = default
        self.map = map
    
    def __getitem__(self, key):
        return self.map.get(key, self.default)
    
    def __setitem__(self, key, value):
        self.map[key] = value
    
    def __delitem__(self, key):
        del self.map[key]

