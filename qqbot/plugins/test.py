from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import asyncio

from .default.api import utils

inc_cmd = on_command("inc" , priority = 10, block = True)
reset_cmd = on_command("reset" ,  priority = 10, block = True)

val = 0

@utils.sync
async def inc(num : int):
    global val
    if num > 1000:
        await inc_cmd.finish(f"Too big input!")
    for i in range(num):
        val += 1
        await asyncio.sleep(0.01)

@inc_cmd.handle()
async def test_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    num = int(event.get_plaintext().split()[1])
    await inc(num)
    await inc_cmd.finish(f"Cur Num : {val}.")

@utils.sync
async def reset():
    global val
    val = 0

@reset_cmd.handle()
async def test_2_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    await reset()
    await reset_cmd.finish(f"Reset to {val}.")