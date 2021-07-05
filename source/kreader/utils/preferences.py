import json
import os


class _WrapNode(object):
    _isfrozen = False

    def __init__(self, setter, data, path):
        self.setter = setter
        self.data = data
        self.path = path
        self._isfrozen = True
    
    def __getattr__(self, name):
        if name in dir(self):
            return self.__getattribute__(name)
        return self[name]
    
    def __getitem__(self, name):
        value = self.data[name]
        if isinstance(value, (int, bool, float, complex, str)):
            return value
        else:
            return _WrapNode(self.setter, value, self.path + [ name ])
    
    def __setitem__(self, name, value):
        self.setter(self.path + [name], value)
    
    def __setattr__(self, name, value):
        if not self._isfrozen:
            object.__setattr__(self, name, value)
        else:
            self[name] = value
    
    def __add__(self, other):
        return self.data + other
    
    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return repr(self.data)


class PreferencesManager(object):
    def __init__(self, path):
        self.path = path
        self._cached_data = None
        self._changes_made = False
    
    def __getattr__(self, name):
        if name in vars(self):
            return self.__getattribute__(name)
        return self[name]
    
    def __getitem__(self, name):
        return self._cached[name]
    
    def __setitem__(self, name, value, save=False):
        self._cached[name] = value
        self._changes_made = True
        if save:
            self.dump_changed()
    
    def read_prefs(self):
        self._cached_data = json.loads(open(self.path, 'rb').read())
        self._changes_made = False
    
    def dump_changes(self):
        if self._changes_made:
            data = json.dumps(self._cached, indent=4)
            open(self.path, 'w').write(data)
            self._changes_made = False
    
    def direct_dump(self, data):
        self._changes_made = True
        self._cached_data = data
        self.dump_changes()
    
    @property
    def _cached(self):
        if self._cached_data is None:
            self.read_prefs()
        return self._cached_data

    @property
    def exists(self):
        return os.path.exists(self.path)
    
    @property
    def edit(self):
        return _WrapNode(self._set_deep, self._cached, [])
    
    def _set_deep(self, path, value):
        node = self
        for name in path[:-1]:
            node = node[name]
        node[path[-1]] = value
        self._changes_made = True

