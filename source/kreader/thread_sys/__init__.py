from typing import Callable, List, NamedTuple, Dict, Tuple
import asyncio
import threading
import queue
import inspect
import types

# Task that is handed to the Handler thread's listener loop
Task = NamedTuple( 'Task', [ ('coroutine', asyncio.Future), ('completion_event', asyncio.Event), ('cancel_event', threading.Event), ('exception_occcurred', threading.Event), ('comms', asyncio.Queue) ] )

# Holds all data that could ever be needed about a Handler
HandlerItem = NamedTuple('HandlerItem', [ ('name', str), ('handler', 'Handler'), ('init_event', asyncio.Event), ('thread', threading.Thread) ] )


class AwaitableItem:
    '''Returned by a Handler and listens for the task to complete on the other thread'''
    def __init__(self, completion_event: asyncio.Event, cancel_event: threading.Event, exception_occurred: threading.Event, communication_queue: asyncio.Queue):
        self.completion_event = completion_event
        self.cancel_event = cancel_event
        self.exception_occurred = exception_occurred
        self.communication_queue = communication_queue
    
    async def _run(self):
        coroutine: asyncio.Future = None
        try:
            coroutine = await self.communication_queue.get() # First item will be the coroutine
            await self.completion_event.wait()
            result = await self.communication_queue.get() # Second item will be the actual output of the coroutine
            if self.exception_occurred.is_set():
                raise result
            return result
        except asyncio.CancelledError:
            self.cancel_event.set() # If the coroutine hasn't started yet, it won't ever

            if not self.communication_queue.empty and coroutine is None: # In case the coroutine hasn't been sent in yet wait for it
                coroutine= await self.results.get()
            
            if coroutine is not None:
                coroutine.cancel()
            
            raise

    def __await__(self):
        return self._run().__await__()
    
    async def __aenter__(self):
        await self._run()
    
    def __call__(self):
        return self._run()
    
    async def __aexit__(self, *args):
        pass


class Handler:
    '''Basically runs a listener loop in a Thread'''
    def __init__(self, name: str):
        self.name = name
        self._tasks: Dict[Task, asyncio.Task] = {}

    def init(self):
        self.loop = asyncio.new_event_loop()
        self.queue = queue.Queue()
        
        if hasattr(self, 'init_event'):
            self.init_event.set()
        
        self.loop.run_until_complete(self._listen())
    
    async def _listen(self):
        while True:
            # Check if tasks have been queued
            try:
                task: Task = self.queue.get_nowait()
                if task.cancel_event.is_set():
                    task.comms.put_nowait(None)
                else:
                    coroutine_task = self.loop.create_task( self._run_task(task) )
                    self._tasks[task] = coroutine_task
                    task.comms.put_nowait(coroutine_task)
            except queue.Empty:
                pass
            
            # Check if anything was cancelled after it was scheduled
            to_delete = []
            for task, coroutine in self._tasks.items():
                if task.cancel_event.is_set():
                    coroutine.cancel()
                    to_delete.append(task)
            
            for task in to_delete:
                del self._tasks[task]
            
            await asyncio.sleep(0)
    
    async def _run_task(self, task: Task):
        coroutine = task.coroutine
        
        if not inspect.isawaitable(coroutine): # If the function hasn't been called, call it here
            coroutine = coroutine()
        try:
            result = await coroutine
            task.comms.put_nowait(result)
            task.completion_event.set()
        except Exception as esc:
            task.exception_occcurred.set()
            task.comms.put_nowait(esc)
        del self._tasks[task]
    
    def set_init_event(self, event: threading.Event):
        self.init_event = event
    
    def __call__(self, coroutine: types.CoroutineType):
        completion_event = asyncio.Event()
        cancel_event = threading.Event()
        exception_occurred = threading.Event()
        communication_queue = asyncio.Queue(maxsize=2) # Item 1 -> Coroutine, Item 2 -> Result
        self.queue.put( Task(coroutine, completion_event, cancel_event, exception_occurred, communication_queue ) )
        return AwaitableItem(completion_event, cancel_event, exception_occurred, communication_queue)

    @staticmethod
    def create_handler(name):
        new_handler = Handler(name)
        init_event = threading.Event()
        new_handler.set_init_event(init_event)
        return new_handler, init_event


def run_in_handler(handler: Handler, func: Callable, communicaton: Tuple[asyncio.Event, asyncio.Queue] = None):
    '''
    Throws a function onto a handler
    It is assumed that the function being run is synchronous
    Because otherwise there is no reason to do this
    '''
    async def curr_thread_task():
        async def other_thread_task():
            return func()
        # The other_thread_task is not called here because then
        # it would be run on the current thread
        result = await handler(other_thread_task)
        if communicaton is not None:
            communicaton[1].put_nowait(result)
            communicaton[0].set()
    asyncio.create_task(curr_thread_task())

async def init_handlers(handler_names, handler_cls=None, debug=False) -> List[HandlerItem]:
    '''
    Takes in a list of handlers and creates handlers with those names
    Also, specific Handler classes can be passed in for any handlers,
    that are special
    '''

    handler_cls = handler_cls if handler_cls is not None else {} # Initialize it to a empty dict if it isn't passed in

    handlers = {}
    for name in handler_names:
        cls_to_instantiate = handler_cls.get(name, Handler)
        handlers[name] = cls_to_instantiate.create_handler(name)
    
    threads = { name: threading.Thread(target=handler.init, daemon=True) for name, (handler, _) in handlers.items() }

    for _, init_task in threads.items():
        init_task.start()
    
    for handler, init_event in handlers.values():
        if debug:
            print('Waiting init event for', handler)
        init_event.wait()
    
    if debug:
        print('waiting finished')
    
    return [ HandlerItem(name, handler, init_event, threads[name]) for name, (handler, init_event) in handlers.items() ]

