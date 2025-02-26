from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import os
import time
import random as rnd

LIB_FOLDER = os.path.join(os.path.dirname(__file__) , "libs")

choose = on_command("random", force_whitespace = " ", priority=10, block=False)

@choose.handle()
async def choose_handle(event : MessageEvent | GroupMessageEvent):
    rnd.seed(time.time())
    ori = event.get_plaintext()[8:].strip() + ' '
    tmp = ""
    is_str = False
    items = []
    i = 0
    while i < len(ori):
        if ori[i] == '"' and tmp == "":
            is_str = True
            i += 1
            continue
        if ori[i] == '"' and ori[i + 1] == ' ':
            items.append(tmp)
            i += 2
            is_str = False
            tmp = ""
            continue
        if ori[i] == '"' and ori[i + 1] != ' ':
            if isinstance(event , GroupMessageEvent):
                await choose.finish(MessageSegment.at(event.user_id) + " 的输入有误！")
            else:
                await choose.finish("输入有误！")
        if ori[i] == '\\' and ori[i + 1] == '"' and is_str:
            tmp += '"'
            i += 2
            continue
        if ori[i] == ' ' and is_str:
            tmp += ' '
            i += 1  
            continue
        if ori[i] == ' ':
            if '-' in tmp:
                tmp = tmp.split('-')
                items.append((int(tmp[0]) , int(tmp[1])))
            else:
                items.append(tmp)
            tmp = ""
            i += 1
            continue
        tmp += ori[i]
        i += 1
    if len(items) == 0:
        if isinstance(event , GroupMessageEvent):
            await choose.finish(MessageSegment.at(event.user_id) + " 的输入有误！")
        else:
            await choose.finish("输入有误！")
    item = items[rnd.randint(0 , len(items) - 1)]
    if type(item) == tuple:
        item = rnd.randint(item[0] , item[1])
    if item[0] == "$":
        if os.path.exists(r"%s\%s.txt"%(LIB_FOLDER , item[1:].strip())):
            f = open(os.path.join(LIB_FOLDER , "%s.txt"%(item[1:])) , encoding="utf-8")
            values = f.read().strip().split("\n")
            f.close()
            item = values[rnd.randint(0 , len(values) - 1)]
    if isinstance(event , GroupMessageEvent):
        await choose.finish(MessageSegment.at(event.user_id) + " 的随机选择的结果为：\n%s"%(item))
    else:
        await choose.finish("随机选择的结果为：\n%s"%(item))
