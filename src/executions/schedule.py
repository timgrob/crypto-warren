import asyncio
from collections.abc import Callable


class AsyncScheduler:
    def __init__(self):
        self.tasks = []

    def schedule(self, task: Callable, *args, **kwargs):
        self.tasks.append((task, args, kwargs))

    async def run(self):
        await asyncio.gather(*(asyncio.create_task(task(*args, **kwargs)) for task, args, kwargs in self.tasks))
