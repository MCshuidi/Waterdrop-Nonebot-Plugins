from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

import os
import time
import asyncio

from . import utils

fin = open(os.path.join(os.path.dirname(__file__) , "strawberry.cfg"))
data = fin.read().split("\n")
fin.close()

api_id = int(data[0].split("=")[1])
api_perfix = data[1].split("=")[1]

@utils.sync(flag = "strawberry")
async def berrycheck_api(bot : Bot , user_id : int , threshold : int) -> bool:
    manager = BerryManager()
    manager.berry_list[user_id] = [0 , asyncio.Event() , None]
    manager.berry_list[user_id][1].clear()
    await bot.send_group_msg(group_id = api_id , message = f".berry_check {api_perfix} {user_id} {threshold}")
    await manager.berry_list[user_id][1].wait()
    ret = manager.berry_list[user_id][2]
    manager.berry_list[user_id] = False
    return ret

@utils.sync(flag = "strawberry")
async def berrychange_api(bot : Bot , user_id : int , berry_num : int) -> bool:
    manager = BerryManager()
    manager.berry_list[user_id] = [1 , asyncio.Event() , None]
    await bot.send_group_msg(group_id = api_id , message = f".berry_change {api_perfix} {user_id} {berry_num}")
    await manager.berry_list[user_id][1].wait()
    ret = manager.berry_list[user_id][2]
    manager.berry_list[user_id] = False
    return ret

######################################################################################################

berrycheck_cmd = on_command("berry_check_finish", force_whitespace = " ", priority = 10, block = True)
berrychange_cmd = on_command("berry_change_finish", force_whitespace = " ", priority = 10, block = True)

@berrycheck_cmd.handle()
async def berrycheckfinish_handler(bot : Bot , event : MessageEvent | GroupMessageEvent):
    manager = BerryManager()
    texts = event.get_plaintext().split()
    if int(texts[1]) not in manager.berry_list.keys() or manager.berry_list[int(texts[1])] == False:
        return
    manager.berry_list[int(texts[1])][2] = texts[3] == "True"
    await asyncio.sleep(1)
    manager.berry_list[int(texts[1])][1].set()

@berrychange_cmd.handle()
async def berrycheckfinish_handler(bot : Bot , event : MessageEvent | GroupMessageEvent):
    manager = BerryManager()
    texts = event.get_plaintext().split()
    if int(texts[1]) not in manager.berry_list.keys() or manager.berry_list[int(texts[1])] == False:
        return
    manager.berry_list[int(texts[1])][2] = texts[3] == "True"
    await asyncio.sleep(1)
    manager.berry_list[int(texts[1])][1].set()

def berrylist_check(self , user_id : int) -> bool:
    return user_id in BerryManager().berry_list

@utils.singleton
class BerryManager:
    def __init__(self):
        self.berry_list : dict[int , list[int , asyncio.Event , bool] | bool] = {}