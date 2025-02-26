import asyncio

def sync(func):
    async def wrapper(*args , **kwargs):
        if not hasattr(sync , "g_lock"):
            sync.g_lock = asyncio.Lock()
        async with sync.g_lock:
            result = await func(*args , **kwargs)
        return result
    return wrapper