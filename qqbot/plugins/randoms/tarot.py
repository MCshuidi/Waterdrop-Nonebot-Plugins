from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment, Bot

import os
import time
import random as rnd

LIB_FOLDER = os.path.join(os.path.dirname(__file__) , "libs" , "tarots")

tarot = on_command("tarot", priority=10, block=False)

@tarot.handle()
async def tarot_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    pass
