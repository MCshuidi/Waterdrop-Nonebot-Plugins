from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import random as rnd

TEXT_LEN_LIMIT = 356

ULTRA_TEMPLATE = "不要再%s了！%s是%s研发的新型鸦片！%s往你的电脑里安装大炮，当你%s时大炮就会被引燃！真是细思极恐！"

ultra = on_command("ultra", force_whitespace = " ", priority=10, block=False)

@ultra.handle()
async def ultra_handle(event : MessageEvent | GroupMessageEvent):
    args = event.get_plaintext()[6:].strip().split()
    if len(args) == 0:
        args = ["ultra" , "加拿大人"]
    if len(args) == 2:
        string = ULTRA_TEMPLATE%(args[0] , args[0] , args[1] , args[1] , args[0])
    else:
        await ultra.finish("参数有误！")
    if len(string) >= TEXT_LEN_LIMIT:
        await ultra.finish("文本过长！")
    await ultra.finish(string)

