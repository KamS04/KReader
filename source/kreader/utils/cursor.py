from queue import Empty, Queue
from kivy.core.window import Window
from kivy.clock import Clock

NORMAL = 'arrow'
POINTER = 'hand'
LOADING = 'wait'

NONE_PRIORITY = -1
NO_PRIORITY = 0
LOW_PRIORITY = 1
HIGH_PRIORITY = 2


class CursorController:
    reset_flag = False
    cursor_type = None
    cursor_prior = -1

    def __init__(self):
        self._cursor_queue = Queue()
        Clock.schedule_interval(self._check, 0)

    def set_cursor(self, cursor, priority=NO_PRIORITY):
        self._cursor_queue.put_nowait( (cursor, priority) )
    
    def reset(self):
        self.reset_flag = True    
    
    def _check(self, *args):
        if self._cursor_queue.empty():
            if self.reset_flag:
                Window.set_system_cursor(NORMAL)
        else:
            cursor, prior = None, NONE_PRIORITY
            while True:
                try:
                    ncur, nprior = self._cursor_queue.get_nowait()
                    if nprior > prior:
                        cursor = ncur
                except Empty:
                    break
            Window.set_system_cursor(cursor)
        self.reset_flag = False

