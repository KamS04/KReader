import asyncio
import inspect
from typing import Awaitable, Callable, List, Union, Coroutine

class Scope:
    def __init__(self):
        self._running: List[asyncio.Task] = []

    def launch(self, coroutine: Union[ Awaitable, Callable[ [], Awaitable ] ]):
        if not inspect.isawaitable(coroutine):
            coroutine = coroutine()
        task = asyncio.create_task(coroutine)
        self._running.append(task)
    
    def cancel_all(self):
        for task in self._running:
            task.cancel()
        self._running = []

