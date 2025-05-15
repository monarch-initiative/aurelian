import asyncio
from typing import Callable, Coroutine


def run_sync(f: Callable | Coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if isinstance(f, Coroutine):
        result = f
    else:
        result = f()

    # Ensure it's a coroutine before running it
    if asyncio.iscoroutine(result):
        result = loop.run_until_complete(result)

    loop.close()
    return result
