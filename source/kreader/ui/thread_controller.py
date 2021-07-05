import queue

from ..thread_sys.manager import start_manager_thread


class LocalThreadController:
    def __init__(self, debug):
        self.tasks_queue = queue.Queue()
        self.results_queue = queue.Queue()
        self.kill_queue = queue.Queue()
        self.debug = debug
    
    def start_manager(self):
        self._manager_thread = start_manager_thread(self.tasks_queue, self.results_queue, self.kill_queue, self.debug)

    def kill(self):
        self.kill_queue.put(None)
