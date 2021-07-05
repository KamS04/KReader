from math import e
import queue
import threading
import ctypes
import inspect

from .coms import Action, ACTION_SCHEDULE, ACTION_TERMINATE, Result

class StopThread(Exception):
    pass

def _async_raise(tid, exctype):
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class ThreadWithExc(threading.Thread):
    def _get_my_tid(self):
        if not self.isAlive():
            raise threading.ThreadError("the thread is not active")

        if hasattr(self, "_thread_id"):
            return self._thread_id
        
        for tid, tobj in threading._active.items():
            if tobj is self:
                self._thread_id = tid
                return tid
                
        raise AssertionError("could not determine the thread's id")

    def raiseExc(self, exctype):
        _async_raise( self._get_my_tid(), exctype )

def manager_function(tasks_queue: queue.Queue, results_queue: queue.Queue, kill_queue: queue.Queue, debug):
    worker_results = queue.Queue()
    threads_map = {}

    # Mainloop listens for everything and keeps the thread alive
    while True:
        # Listen for a "poision pil", once received terminate all subprocesses and stop self
        try:
            poison_pill = kill_queue.get(timeout=1)
            if debug: print('Received Poison Pill')

            for task_id, thread in threads_map.items():
                thread.raiseExc(StopThread)
            
            break
        except queue.Empty:
            pass
        except Exception as e:
            raise e
            

        # Listen for tasks, create processes for them, start the new thread
        while True:
            try:
                action: Action = tasks_queue.get(block=True, timeout=1)
                if action.action_type == ACTION_SCHEDULE:
                    worker_thread = ThreadWithExc(target=action.task.execute, args=(worker_results,), daemon=True)
                    
                    threads_map[action.task.task_id] = worker_thread
                    worker_thread.start()

                    if debug: print('Task scheduled', action.task)
                elif action.action_type == ACTION_TERMINATE:
                    worker_thread: ThreadWithExc = threads_map.get(action.task.task_id, None)

                    if worker_thread is not None:
                        worker_thread.raiseExc(StopThread)
                        del threads_map[action.task.task_id]

                    if debug: print('Terminating Task', action.task)
                
                tasks_queue.task_done()
            except queue.Empty:
                break
            except Exception as e:
                raise e
        
        # Listen for results, send results to main process
        # Check if we should stop trackign the process the result came from
        while True:
            try:
                result: Result = worker_results.get(block=True, timeout=1)
                if debug: print('Result received', result)

                if result.task_id in threads_map.keys():
                    if result.task_finished:
                        del threads_map[result.task_id]
                    
                    if result.should_put:
                        results_queue.put(result)
                elif debug:
                    print('Task for', result, 'was already cancelled')
            
            except queue.Empty:
                break
            except Exception as e:
                raise e
    
    return

def start_manager_thread(tasks_queue: queue.Queue, results_queue: queue.Queue, kill_queue: queue.Queue, debug=True):
    manager_thread = threading.Thread(target=manager_function, args=(tasks_queue, results_queue, kill_queue, debug), daemon=True)
    manager_thread.start()
    return manager_thread