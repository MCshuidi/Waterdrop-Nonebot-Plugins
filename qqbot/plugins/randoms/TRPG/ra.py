from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment, Bot

import re

ra_dice = on_command("ra" , force_whitespace = "")

skill_re = re.compile(r".(ra)(.*?)(\d*)$")

result_texts = [
    
]

@ra_dice.handle()
async def ra_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    print(await bot.get_stranger_info(user_id = event.get_user_id()))
    text = event.get_plaintext()
    result = re.match(skill_re , text)
    if result == None:
        return
    #ra_dice.finish(f"正在为[{bot.}]进行技能[{}:{}]的检定。\n1D100={}/{} \n{}")