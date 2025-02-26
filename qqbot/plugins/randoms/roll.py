from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import random as rnd

roll = on_command("roll", force_whitespace = " ", priority=10, block=False)

class Dice:
    def __init__(self , d):
        self.l = 1
        self.r = d
    def roll(self):
        return rnd.randint(self.l , self.r)

@roll.handle()
async def roll_handle(event : MessageEvent | GroupMessageEvent):
    dices = []
    C = 0
    text = event.get_plaintext()[6:].strip()
    if text == "":
        text = "d6"
    text += "|"
    tmp = ""
    for c in text:
        if c in "+-" and tmp == "":
            tmp += c
        elif c in "+-|" and "d" not in tmp:
            C += int(tmp)
            tmp = c
        elif c in "+-|" and "d" in tmp:
            try:
                if tmp[0] == "d":
                    tmp = (1 ,int(tmp[1:]))
                elif tmp[0:2] == "+d":
                    tmp = (1 ,int(tmp[2:]))
                elif tmp[0:2] == "-d":
                    tmp = (-1 ,int(tmp[2:]))
                else:
                    tmp = list(map(int , tmp.split("d")))
                if len(tmp) != 2:
                    await roll.finish("输入错误！")
                if tmp[1] > 2147483647 or tmp[1] <= 1:
                    await roll.finish("骰子面数错误！")
                if len(dices) + tmp[0] > 50:
                    await roll.finish("骰子数量过多！")
            except ValueError:
                await roll.finish("输入错误！")
            dices.extend([(tmp[0] < 0, Dice(tmp[1])) for i in range(abs(tmp[0]))])
            tmp = c
        elif c.isdigit() or c.lower() == "d":
            tmp += c
        elif c == " ":
            continue
        else:
            await roll.finish("输入包含了除了数字，加减号和d以外的符号！")
    if len(str(C)) > 12:
        await roll.finish("常数过大！")
    tmp = ""
    sum_ = 0
    for pair in dices:
        val = pair[1].roll()
        if pair[0]:
            sum_ -= val
            tmp += " - %d"%(val)
        else:
            sum_ += val
            if tmp == "":
                tmp += "%d"%(val)
            else:
                tmp += " + %d"%(val)
    if not ((len(dices) == 1 and C == 0) or (len(dices) == 0)):
        if C == 0:
            tmp = "%s = %d"%(tmp , sum_)
        else:
            tmp = "%s + %d = %d"%(tmp , C , sum_ + C)
    elif len(dices) == 0:
        tmp = "%d"%(C)
    if isinstance(event , GroupMessageEvent):
        await roll.finish(MessageSegment.at(event.user_id) + "的掷骰结果为：\n%s"%(tmp))
    else:
        await roll.finish("掷骰结果为：\n%s"%(tmp))
