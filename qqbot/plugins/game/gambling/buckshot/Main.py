from nonebot import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

MAX_ITEM_COUNT = 8
MAX_ALL_HEART = 12

shoot_command = on_command("shoot" , aliases = ["射击" , "开枪"] , force_whitespace = None)
use_item_command = on_command("use" , aliases = ["使用"] , force_whitespace = None)
check_item_command = on_command("check" , aliases = ["查询"] , force_whitespace = None)

