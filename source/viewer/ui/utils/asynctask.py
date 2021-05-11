from kivy.clock import Clock
from threading import Thread
from functools import partial

class AsyncTask:
    '''
    onfinish will receive the following arguments
    obj (if the onfinish task was something like 'self.onfinish'), *arguments defined in lambda or partial, result from task, time_delta
    '''

    def __init__(self, task: 'function', on_finish: 'function' = None):
        self.task = task
        self.on_finish = on_finish
        self._thread = None
        self.is_cancelled = False

    def start(self):
        self._thread = Thread(target=self.run_task, daemon=True)
        self._thread.start()
    
    def run_task(self, *args):
        result = self.task()
        if self.on_finish is not None and not self.is_cancelled:
            Clock.schedule_once(partial(self.on_finish, result), 0)
    
    def cancel_task(self):
        self.is_cancelled = True

class AsyncStreamTask:
    '''
    onfinish will receive the following arguments
    obj (if the onfinish task was something like 'self.onfinish'), *arguments defined in lambda or partial, result from task, time_delta
    '''

    def __init__(self, task: 'function', on_update: 'function'=None, on_finish: 'function' = None):
        self.task = task
        self.on_update = on_update
        self.on_finish = on_finish
        self._thread = None
        self.is_cancelled = False

    def start(self):
        self._thread = Thread(target=self.run_task, daemon=True)
        self._thread.start()
    
    def run_task(self, *args):
        for result in self.task():
            if self.on_update is not None and not self.is_cancelled:
                Clock.schedule_once(partial(self.on_update, result), 0)
        if self.on_finish is not None:
            Clock.schedule_once(self.on_finish, 0)
    
    def cancel_task(self):
        self.is_cancelled = True

