from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment, Bot

import random as rnd
import time
import re

ra_dice = on_command("ra")

skill_re = re.compile(r".(ra)(\s*)(.*?)(\d+)$")
skill2_re = re.compile(r".(ra)(\s*)(.*?)((\d+)(.+))$")

result_texts = [
    # 大成功
    ["大成功！不愧是你！",
     "哇，大成功！想好今天吃什么了吗？",
     "幸运女神附身了，是大成功！"],
    # 极难成功
    ["极难成功！事情发展一定很顺利吧！",
     "居然是极难成功耶，运气真好！",
     "哇，极难成功啊！",
     "极难成功！这应该足够通过大多数检定了！"],
    # 困难成功
    ["困难成功欸，这是一个好兆头呢！",
     "困难成功！好，很好，非常好！",
     "困难成功，我们又战胜了一道难关！",
     "是一个困难成功哦！"],
    # 一般成功
    ["看起来是一次很普通的成功呢。",
     "一次很普通的的普通成功！",
     "是普通的成功，再加把力哦！"],
    # 失败
    ["啊呀，一次普通的失败。",
     "失败了呢，没准下一次就成功了！",
     "失败是成功之母，下次就成功了！"],
    # 大失败
    ["大失败啊！难道真是……天命难违？",
     "大失败……这是骰子灌铅了？",
     "哎呀，是大失败，要是个位骰不是0而是1那就是另一种结果了……"],
]

@ra_dice.handle()
async def ra_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    text = event.get_plaintext()
    result = re.match(skill_re , text).groups()
    if result == None:
        result = re.match(skill2_re , text).groups()
        if result == None:
            return
        type = result[2]
        point = int(result[4])
    else:
        type = result[2]
        point = int(result[3])
    rnd.seed(time.time())
    dice = rnd.randint(1 , 100)
    if dice <= 5:
        r_type = rnd.choice(result_texts[0])
    elif dice <= point // 5:
        r_type = rnd.choice(result_texts[1])
    elif dice <= point // 2:
        r_type = rnd.choice(result_texts[2])
    elif dice <= point:
        r_type = rnd.choice(result_texts[3])
    elif dice >= 96:
        r_type = rnd.choice(result_texts[5])
    else:
        r_type = rnd.choice(result_texts[4])
    ra_dice.finish(f"正在为[{bot.get_stranger_info(user_id = event.get_user_id())["nick"]}]进行技能[{type}:{point}]的检定。\n1D100={dice}/{point} \n{r_type}")