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
    
    def start(self):
        Thread(target=self.run_task, daemon=True).start()
    
    def run_task(self, *args):
        result = self.task()
        if self.on_finish is not None:
            Clock.schedule_once(partial(self.on_finish, result), 0)