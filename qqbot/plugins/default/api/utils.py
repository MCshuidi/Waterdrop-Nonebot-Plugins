import asyncio

def sync(flag = "global"):
    def deco(func):
        async def wrapper(*args , **kwargs):
            if not hasattr(sync , f"{flag}_lock"):
                setattr(sync , f"{flag}_lock" , asyncio.Lock())
            async with getattr(sync , f"{flag}_lock"):
                result = await func(*args , **kwargs)
            return result
        return wrapper
    return deco

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance