from typing import Generic, TypeVar
from threading import Lock

T = TypeVar("T")

class LockingObject(Generic[T]):
    def __init__(self, obj: T, lock: Lock = None):
        self._lock = lock if lock is not None else Lock()
        self._obj = obj
    
    def __enter__(self, *args) -> T:
        #print('lockingobject#enter', *args)
        self._lock.acquire()
        return self._obj
    
    def __exit__(self, *args):
        #print('locingobject#exit', *args)
        self._lock.release()

