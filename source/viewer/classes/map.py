from typing import Any


class DefaultingMap:
    def __init__(self, data_map: dict, default: Any):
        self.map = data_map
        self.default = default
    
    def __getitem__(self, key):
        if key in self.map.keys():
            return self.map[key]
        return self.default

