from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import sys
from io import StringIO

execute = on_command("exec", force_whitespace = " ", priority=10, block=False)

variables = {}

@execute.handle()
async def execute_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    cmd  = " ".join(event.get_plaintext().split()[1:])
    try:
        output = StringIO()
        sys.stdout = output
        exec(cmd , variables)
        sys.stdout = sys.__stdout__
    except Exception as e:
        await execute.finish(str(e))
    if output.getvalue() == "":
        return
    await execute.finish(output.getvalue().strip())