from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import re
import os
import time
import random as rnd

pattern_obj_1 = re.compile(r"(.+?)(\s)|(.+)")
pattern_obj_2 = re.compile(r"\"(.+?)\"")

pattern_dice = re.compile(r".*(\[(1d(\d+(\+\d+)?))\]).*")

LIB_FOLDER = os.path.join(os.path.dirname(__file__) , "libs" , "choose")

choose = on_command("random", force_whitespace = " ", priority=10, block=False)

@choose.handle()
async def choose_handle(event : MessageEvent | GroupMessageEvent):
    rnd.seed(time.time())
    ori = event.get_plaintext()[8:].strip() + ' '
    items = []
    i = 0
    while i < len(ori):
        res = re.match(pattern_obj_1 , ori[i:])
        if res is not None:
            if res[0] is not None:
                items.append(res[0])
                i += len(res.group())
                continue
            else:
                items.append(res[2])
                i += len(res.group())
                continue
        res = re.match(pattern_obj_2 , ori[i:])
        if res is not None:
            items.append(res[0])
            i += len(res.group())
            continue
        await choose.finish("输入有误！")
    if len(items) == 0:
        if isinstance(event , GroupMessageEvent):
            await choose.finish(MessageSegment.at(event.user_id) + " 的输入有误！")
        else:
            await choose.finish("输入有误！")
    item = items[rnd.randint(0 , len(items) - 1)]
    if type(item) == tuple:
        item = rnd.randint(item[0] , item[1])
    if item[0] == "$":
        if os.path.exists(r"%s/%s.txt"%(LIB_FOLDER , item[1:].strip())):
            f = open(os.path.join(LIB_FOLDER , "%s.txt"%(item[1:].strip())) , encoding="utf-8")
            values = f.read().strip().split("\n")
            f.close()
            item = values[rnd.randint(0 , len(values) - 1)]
    if re.match(pattern_dice , item):
        res = re.match(pattern_dice , item).groups()
        item.replace(res[0] , str(rnd.randint(1 , eval(res[2]))))
        item.replace("\\n" , "\n")
    if isinstance(event , GroupMessageEvent):
        await choose.finish(MessageSegment.at(event.user_id) + " 的随机选择的结果为：\n%s"%(item))
    else:
        await choose.finish("随机选择的结果为：\n%s"%(item))
