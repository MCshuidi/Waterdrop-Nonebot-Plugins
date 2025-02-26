from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import random as rnd

POKE = [("黑桃", "梅花", "方块", "红心") , ("A" , "2" , "3" , "4" , "5" , "6" , "7" , "8" , "9" , "10" , "J" , "Q" , "K")]
STANDING = {}

blackjack = on_command("blackjack", force_whitespace = " ", priority=10, block=False)

@blackjack.handle()
async def blackjack_handle(event : MessageEvent | GroupMessageEvent):
    pass