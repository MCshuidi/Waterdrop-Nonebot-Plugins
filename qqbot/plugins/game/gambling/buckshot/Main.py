from nonebot import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

MAX_ITEM_COUNT = 8
MAX_ALL_HEART = 12

shoot_command = on_startswith("开枪")