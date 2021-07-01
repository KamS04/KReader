from typing import Any


class DefaultingDict(dict):
    def __init__(self, default: Any, *args, **kwargs):
        super(DefaultingDict, self).__init__(*args, **kwargs)
        self.default = default
    
    def __getitem__(self, key):
        return self.get(key, self.default)
