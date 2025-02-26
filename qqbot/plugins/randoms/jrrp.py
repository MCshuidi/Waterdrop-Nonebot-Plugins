from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import time
import hashlib
import random as rnd

RPS = [
    (42,42,"感觉可以参透宇宙的真理。"),
    (74,74,"适合去旅馆探险。"),
    (0 ,0 ,"怎么会这样..."),
    (1 ,20,"推荐闷头睡大觉。"),
    (21,40,"也许今天适合摆烂。"),
    (41,60,"又是平凡的一天。"),
    (61,80,"太阳当头照，花儿对你笑。"),
    (81,99,"要不要炼个金呢..."),
    (100,100,"买彩票可能会中大奖哦。"),
    ]

jrrp = on_command("jrrp", force_whitespace = "", priority=10, block=False)

@jrrp.handle()
async def jrrp_handle(event : MessageEvent | GroupMessageEvent):
    if isinstance(event , GroupMessageEvent):
        uid = event.user_id
        rnd.seed(int(hashlib.sha256(time.strftime("%Y-%m-%d").__add__(str(uid)).encode()).hexdigest(),16))
        rp = rnd.randint(0 ,100)
        for RP in RPS:
            if RP[0] <= rp <= RP[1]:
                break
        await jrrp.finish(MessageSegment.at(event.user_id) + "的今日人品是：%d。%s"%(rp , RP[2]))
    else:
        uid = event.get_user_id()
        rnd.seed(int(hashlib.sha256(time.strftime("%Y-%m-%d").__add__(str(uid)).encode()).hexdigest(),16))
        rp = rnd.randint(0 ,100)
        for RP in RPS:
            if RP[0] <= rp <= RP[1]:
                break
        await jrrp.finish("%s的今日人品是：%d。%s"%(event.sender.nickname , rp , RP[2]))
    
    
