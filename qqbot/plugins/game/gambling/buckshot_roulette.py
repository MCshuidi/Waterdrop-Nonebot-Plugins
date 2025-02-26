from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

import redis
import random as rnd
import time
import datetime

MAX_ITEM_COUNT = 8

DIVIDER = "========================"

P_IDLE = 0x00
P_WAITING = 0x01
P_HOLDING = 0x02
P_LOCKED = 0x03
P_UNLOCKED = 0x04

R_WAITING = 0x10
R_RUNNING = 0x11

AMMO_REAL = 0x20
AMMO_FAKE = 0x21

G_NORMAL = 0x30
G_DOUBLE = 0x31

class Item:
    def __init__(self , name : str , description : str , active , shortcut : str):
        self.name = name
        self.description = description
        self.shortcut = shortcut
        self.active = active
    def use(self):
        return self.active

class Room:
    def __init__(self , g_id : int):
        self.g_id = g_id
        self.c_time : float = 0
        self.rd_st : int = rnd.randint(0 , 1)
        self.p1_id : str = 0
        self.p2_id : str = 0
        self.p1_HP : int = 0
        self.p2_HP : int = 0
        self.p1_state : int = P_IDLE
        self.p2_state : int = P_IDLE
        self.gun_state : int = G_NORMAL
        self.game_state : int = R_WAITING
        self.round : int = 0
        self.ammo : tuple[int] = tuple()
        self.bullets : list[int] = []
        self.p1_items : list[Item] = []
        self.p2_items : list[Item] = []
    async def p1_join(self , bot : Bot , p1_id : int):
        self.p1_id = p1_id
        self.c_time = time.time()
        # Build output Message
        msg = "对局已创建。\n已加入玩家：\n1) "
        msg += MessageSegment.at(self.p1_id)
        msg += "\n2) None"
        await bot.send_group_msg(group_id = self.g_id , message = msg)
    async def p2_join(self , bot : Bot , p2_id) -> None:
        self.p2_id = p2_id
        self.game_state = R_RUNNING
        # Build output Message
        msg = "对局已创建。\n已加入玩家：\n1) "
        msg += MessageSegment.at(self.p1_id)
        msg += "\n2) "
        msg += MessageSegment.at(self.p2_id)
        await bot.send_group_msg(group_id = self.g_id , message = msg)
    def g_start(self , bot : Bot) -> None:
        ori_hp = rnd.randint(4 , 8)
        self.max_hp : list[int] = [ori_hp for i in range(2)]
        self.p1_HP = self.max_hp[0]
        self.p2_HP = self.max_hp[1]
    async def r_start(self , bot : Bot) -> None:
        self.round += 1
        # Set player state
        if (self.round + self.rd_st) % 2 == 1:
            self.p1_state = P_HOLDING
            self.p2_state = P_WAITING
        else:
            self.p1_state = P_WAITING
            self.p2_state = P_HOLDING
        # Reloading
        fakes = rnd.randint(1 , 5)
        self.ammo = (rnd.randint(1 , min(2 * fakes , 4 , 8 - fakes)) , fakes)
        self.bullets = [AMMO_REAL for i in range(self.ammo[0])]
        self.bullets.extend([AMMO_FAKE for i in range(self.ammo[1])])
        rnd.shuffle(self.bullets)
        randitem(self)
        # Build output Message
        msg : str = f"回合开始！\n回合数：{self.round}\n{DIVIDER}\n本轮子弹：\n实弹：{self.ammo[0]}发|虚弹：{self.ammo[1]}发\n{DIVIDER}\n玩家"
        msg += MessageSegment.at(self.p1_id)
        msg += " 的血量是：%d/%d。\n拥有的道具有（%d/8）：\n"%(self.p1_HP , self.max_hp[0] , len(self.p1_items))
        for item in self.p1_items:
            msg += item.name
            msg += "\n"
        msg += DIVIDER
        msg += f"\n"
        msg += MessageSegment.at(self.p2_id)
        msg += " 的血量是：%d/%d。\n拥有的道具（%d/8）有：\n"%(self.p2_HP , self.max_hp[1] , len(self.p2_items))
        for item in self.p2_items:
            msg += item.name
            msg += "\n"
        await bot.send_group_msg(group_id = self.g_id , message = str(msg).strip())
        if self.p1_state == P_HOLDING:
            await bot.send_group_msg(group_id = self.g_id , message = "接下来是" + MessageSegment.at(self.p1_id) + " 的回合。")
        else:
            await bot.send_group_msg(group_id = self.g_id , message = "接下来是" + MessageSegment.at(self.p2_id) + " 的回合。")
    async def r_shoot(self , bot : Bot , p_at : int) -> None:
        ammo = self.bullets.pop(0)
        if self.p1_state == P_HOLDING:
            if ammo == AMMO_REAL:
                if p_at == 1:
                    # Dec HP
                    if self.gun_state == G_DOUBLE:
                        self.p1_HP -= 2
                    else:
                        self.p1_HP -= 1
                    # Judge Lock
                    if self.p2_state == P_LOCKED:
                        self.p2_state = P_UNLOCKED
                    else:
                        self.p1_state = P_WAITING
                        self.p2_state = P_HOLDING
                    # Build output Message
                    msg = MessageSegment.at(self.p1_id)
                    if self.gun_state == G_DOUBLE:
                        msg += " 选择射击自己。轰！你中了一枪。\n"
                    else:
                        msg += " 选择射击自己。砰！你中了一枪。\n"
                    msg += f"自己剩余生命：{self.p1_HP}。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
                else:
                    # Dec HP
                    if self.gun_state == G_DOUBLE:
                        self.p2_HP -= 2
                    else:
                        self.p2_HP -= 1
                    # Judge Lock
                    if self.p2_state == P_LOCKED:
                        self.p2_state = P_UNLOCKED
                    else:
                        self.p1_state = P_WAITING
                        self.p2_state = P_HOLDING
                    # Build output Message
                    msg = MessageSegment.at(self.p1_id)
                    if self.gun_state == G_DOUBLE:
                        msg += " 选择射击对手。轰！对手中了一枪。\n"
                    else:
                        msg += " 选择射击对手。砰！对手中了一枪。\n"
                    msg += f"对手剩余生命：{self.p2_HP}。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
            if ammo == AMMO_FAKE:
                if p_at == 1:
                    # Build output Message
                    msg = MessageSegment.at(self.p1_id)
                    msg += f" 选择射击自己。咔哒，哎呀，是一发空弹。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
                else:
                    # Judge Lock
                    if self.p2_state == P_LOCKED:
                        self.p2_state = P_UNLOCKED
                    else:
                        self.p1_state = P_WAITING
                        self.p2_state = P_HOLDING
                    # Build output Message
                    msg = MessageSegment.at(self.p1_id)
                    msg += f" 选择射击对手。咔哒，哎呀，是一发空弹。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
        else:
            if ammo == AMMO_REAL:
                if p_at == 1:
                    # Dec HP
                    if self.gun_state == G_DOUBLE:
                        self.p1_HP -= 2
                    else:
                        self.p1_HP -= 1
                    # Judge Lock
                    if self.p1_state == P_LOCKED:
                        self.p1_state = P_UNLOCKED
                    else:
                        self.p1_state = P_HOLDING
                        self.p2_state = P_WAITING
                    # Build output Message
                    msg = MessageSegment.at(self.p2_id)
                    if self.gun_state == G_DOUBLE:
                        msg += " 选择射击对手。轰！对手中了一枪。\n"
                    else:
                        msg += " 选择射击对手。砰！对手中了一枪。\n"
                    msg += f"对手剩余生命：{self.p1_HP}。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
                else:
                    # Dec HP
                    if self.gun_state == G_DOUBLE:
                        self.p2_HP -= 2
                    else:
                        self.p2_HP -= 1
                    # Judge Lock
                    if self.p1_state == P_LOCKED:
                        self.p1_state = P_UNLOCKED
                    else:
                        self.p1_state = P_HOLDING
                        self.p2_state = P_WAITING
                    # Build output Message
                    msg = MessageSegment.at(self.p2_id)
                    if self.gun_state == G_DOUBLE:
                        msg += " 选择射击自己。轰！你中了一枪。\n"
                    else:
                        msg += " 选择射击自己。砰！你中了一枪。\n"
                    msg += f"自己剩余生命：{self.p2_HP}。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
            if ammo == AMMO_FAKE:
                if p_at == 1:
                    # Judge Lock
                    if self.p1_state == P_LOCKED:
                        self.p1_state = P_UNLOCKED
                    else:
                        self.p1_state = P_HOLDING
                        self.p2_state = P_WAITING
                    # Build output Message
                    msg = MessageSegment.at(self.p2_id)
                    msg += f" 选择射击对手。咔哒，哎呀，是一发空弹。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
                else:
                    # Build output Message
                    msg = MessageSegment.at(self.p2_id)
                    msg += f" 选择射击自己。咔哒，哎呀，是一发空弹。"
                    await bot.send_group_msg(group_id = self.g_id , message = msg)
        if not self.r_is_end():
            if self.gun_state == G_DOUBLE:
                self.gun_state = G_NORMAL
                await bot.send_group_msg(group_id = self.g_id , message = "枪状态已恢复。")
    async def r_use_item(self , bot : Bot , item_name : str) -> None:
        if self.p1_state == P_HOLDING:
            for i in range(len(self.p1_items)):
                if self.p1_items[i].name == item_name:
                    item = self.p1_items.pop(i)
                    await item.active(bot , self)
                    break
            else:
                await bot.send_group_msg(group_id = self.g_id , message = MessageSegment.at(self.p1_id) + f" 你没有道具：{item_name}！")
        else:
            for i in range(len(self.p2_items)):
                if self.p2_items[i].name == item_name:
                    item = self.p2_items.pop(i)
                    await item.active(bot , self)
                    break
            else:
                await bot.send_group_msg(group_id = self.g_id , message = MessageSegment.at(self.p2_id) + f" 你没有道具：{item_name}！")
    async def r_check(self , bot : Bot):
        msg = f"现在是"
        if self.p1_state == P_HOLDING:
            msg += MessageSegment.at(self.p1_id)
        else:
            msg += MessageSegment.at(self.p2_id)
        msg += f" 的回合。\n"
        if self.p1_state == P_LOCKED:
            msg += MessageSegment.at(self.p1_id)
            msg += " 仍旧被手铐铐着。\n"
        if self.p2_state == P_LOCKED:
            msg += MessageSegment.at(self.p2_id)
            msg += " 仍旧被手铐铐着。\n"
        msg += f"{DIVIDER}\n"
        # "本轮剩余子弹：\n实弹：{self.bullets.count(AMMO_REAL)}发|虚弹：{self.bullets.count(AMMO_FAKE)}发。\n{DIVIDER}\n"
        msg += MessageSegment.at(self.p1_id)
        msg += " 的血量是：%d/%d。\n拥有的道具（%d/8）有：\n"%(self.p1_HP , self.max_hp[0] , len(self.p1_items))
        for item in self.p1_items:
            msg += item.name
            msg += "\n"
        msg += DIVIDER
        msg += "\n"
        msg += MessageSegment.at(self.p2_id)
        msg += " 的血量是：%d/%d。\n拥有的道具（%d/8）有：\n"%(self.p2_HP , self.max_hp[1] , len(self.p2_items))
        for item in self.p2_items:
            msg += item.name
            msg += "\n"
        await bot.send_group_msg(group_id = self.g_id , message = msg)
    def r_is_end(self) -> bool:
        return self.p1_HP <= 0 or self.p2_HP <= 0
    def r_is_turn(self , p_id : str) -> bool:
        if p_id == self.p1_id and self.p1_state == P_HOLDING:
            return True
        if p_id == self.p2_id and self.p2_state == P_HOLDING:
            return True
        return False

def randitem(room : Room):
    TOTAL_POSSIBLY = 0
    for pair in ITEMS:
        TOTAL_POSSIBLY += pair[0]
    item_count = rnd.randint(1 , 4)
    for i in range(item_count):
        if len(room.p1_items) == MAX_ITEM_COUNT:
            break
        p = rnd.randint(1 , TOTAL_POSSIBLY)
        for j in range(len(ITEMS)):
            if p <= ITEMS[j][0]:
                break
            p -= ITEMS[j][0]
        room.p1_items.append(ITEMS[j][1])
    for i in range(item_count):
        if len(room.p2_items) == MAX_ITEM_COUNT:
            break
        p = rnd.randint(1 , TOTAL_POSSIBLY)
        for j in range(len(ITEMS)):
            if p <= ITEMS[j][0]:
                break
            p -= ITEMS[j][0]
        room.p2_items.append(ITEMS[j][1])

async def f_cigarette(bot : Bot , room : Room):
    if room.p1_state == P_HOLDING:
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        if room.p1_HP < room.max_hp[0]:
            msg += f" 使用了道具[香烟]！\n恢复了一点生命值。"
            room.p1_HP = min(room.p1_HP + 1 , room.max_hp[0])
        else:
            msg += f" 使用了道具[香烟]！\n但是生命值是满的，所以什么也没有发生。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        if room.p2_HP < room.max_hp[1]:
            msg += f" 使用了道具[香烟]！\n恢复了一点生命值。"
            room.p2_HP = min(room.p2_HP + 1 , room.max_hp[1])
        else:
            msg += f" 使用了道具[香烟]！\n但是生命值是满的，所以什么也没有发生。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_medicine(bot : Bot , room : Room):
    delta = rnd.randint(1 , 100)
    if room.p1_state == P_HOLDING:
        if delta > 50:
            room.p1_HP -= 1
            # Build output Message
            msg = MessageSegment.at(room.p1_id)
            msg += f" 使用了道具[过期的药]！\n但是药已经过期了，你失去了一点生命值。"
            await bot.send_group_msg(group_id = room.g_id , message = msg)
        else:
            # Build output Message
            msg = MessageSegment.at(room.p1_id)
            if room.p1_HP < room.max_hp[0]:
                msg += f" 使用了道具[过期的药]！\n但是药还有效，你恢复了两点生命值。"
                room.p1_HP = min(room.p1_HP + 2 , room.max_hp[0])
            else:
                msg += f" 使用了道具[过期的药]！\n但是生命值是满的，所以什么也没有发生。"
            await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        if delta > 50:
            room.p2_HP -= 1
            # Build output Message
            msg = MessageSegment.at(room.p2_id)
            msg += f" 使用了道具[过期的药]！\n但是药已经过期了，你失去了一点生命值。"
            await bot.send_group_msg(group_id = room.g_id , message = msg)
        else:
            # Build output Message
            msg = MessageSegment.at(room.p2_id)
            if room.p2_HP < room.max_hp[1]:
                msg += f" 使用了道具[过期的药]！\n但是药还有效，你恢复了两点生命值。"
                room.p2_HP = min(room.p2_HP + 2 , room.max_hp[1])
            else:
                msg += f" 使用了道具[过期的药]！\n但是生命值是满的，所以什么也没有发生。"
            await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_handsaw(bot : Bot , room : Room):
    room.gun_state = G_DOUBLE
    if room.p1_state == P_HOLDING:
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[手锯]！枪的伤害增加到了两点。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[手锯]！枪的伤害增加到了两点。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_inverter(bot : Bot , room : Room):
    room.bullets[0] ^= 1
    if room.p1_state == P_HOLDING:
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[转换器]！下一发子弹的类型被切换了。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[转换器]！下一发子弹的类型被切换了。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_beer(bot : Bot , room : Room):
    ammo = room.bullets.pop(0)
    if ammo == AMMO_FAKE:
        ammo = "虚弹"
    else:
        ammo = "实弹"
    if room.p1_state == P_HOLDING:
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[汽水]！退掉了一发{ammo}。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[汽水]！退掉了一发{ammo}。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_magnifying_glass(bot : Bot , room : Room):
    ammo = room.bullets[0]
    if ammo == AMMO_FAKE:
        ammo = "虚弹"
    else:
        ammo = "实弹"
    if room.p1_state == P_HOLDING:
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[放大镜]！下一发子弹是{ammo}。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[放大镜]！下一发子弹是{ammo}。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_handcuffs(bot : Bot , room : Room):
    if room.p1_state == P_HOLDING:
        if room.p2_state == P_WAITING:
            room.p2_state = P_LOCKED        
            # Build output Message
            msg = MessageSegment.at(room.p1_id)
            msg += f" 使用了道具[手铐]！对手被禁锢一回合。"
            await bot.send_group_msg(group_id = room.g_id , message = msg)
        else:
            room.p1_items.append(ITEMS[6][1])
            await bot.send_group_msg(group_id = room.g_id , message = "同一回合内不能连续使用手铐！")
    else:
        if room.p1_state == P_WAITING:
            room.p1_state = P_LOCKED        
            # Build output Message
            msg = MessageSegment.at(room.p2_id)
            msg += f" 使用了道具[手铐]！对手被禁锢一回合。"
            await bot.send_group_msg(group_id = room.g_id , message = msg)
        else:
            room.p2_items.append(ITEMS[6][1])
            await bot.send_group_msg(group_id = room.g_id , message = "同一回合内不能连续使用手铐！")

async def f_d6(bot : Bot , room : Room):
    TOTAL_POSSIBLY = 0
    for pair in ITEMS:
        TOTAL_POSSIBLY += pair[0]
    if room.p1_state == P_HOLDING:
        item_count = len(room.p1_items)
        room.p1_items = []
        for i in range(item_count):
            p = rnd.randint(1 , TOTAL_POSSIBLY)
            for j in range(len(ITEMS)):
                if p <= ITEMS[j][0]:
                    break
                p -= ITEMS[j][0]
            room.p1_items.append(ITEMS[j][1])
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[D6]！所有道具被重置了。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        item_count = len(room.p2_items)
        room.p2_items = []
        for i in range(item_count):
            p = rnd.randint(1 , TOTAL_POSSIBLY)
            for j in range(len(ITEMS)):
                if p <= ITEMS[j][0]:
                    break
                p -= ITEMS[j][0]
            room.p2_items.append(ITEMS[j][1])
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[D6]！所有道具被重置了。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_d100(bot : Bot , room : Room):
    TOTAL_POSSIBLY = 0
    for pair in ITEMS:
        TOTAL_POSSIBLY += pair[0]
    # Reroll Bullets
    fakes = rnd.randint(0 , max(1 , len(room.bullets) - 1))
    room.ammo = (len(room.bullets) - fakes , fakes)
    room.bullets = [AMMO_REAL for i in range(room.ammo[0])]
    room.bullets.extend([AMMO_FAKE for i in range(room.ammo[1])])
    rnd.shuffle(room.bullets)
    if room.p1_state == P_HOLDING:
        room.p1_HP = rnd.randint(4 , 8)
        room.max_hp[0] = rnd.randint(4 , 8)
        item_count = len(room.p1_items)
        room.p1_items = []
        for i in range(item_count):
            p = rnd.randint(1 , TOTAL_POSSIBLY)
            for j in range(len(ITEMS)):
                if p <= ITEMS[j][0]:
                    break
                p -= ITEMS[j][0]
            room.p1_items.append(ITEMS[j][1])
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[D100]！所有东西都被重置了。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        room.p2_HP = rnd.randint(4 , 8)
        room.max_hp[1] = rnd.randint(4 , 8)
        item_count = len(room.p2_items)
        room.p2_items = []
        for i in range(item_count):
            p = rnd.randint(1 , TOTAL_POSSIBLY)
            for j in range(len(ITEMS)):
                if p <= ITEMS[j][0]:
                    break
                p -= ITEMS[j][0]
            room.p2_items.append(ITEMS[j][1])
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[D100]！所有东西都被重置了。"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_gift(bot : Bot , room : Room):
    TOTAL_POSSIBLY = 0
    for pair in ITEMS:
        TOTAL_POSSIBLY += pair[0]
    item_count = 2
    temp_items : list[Item] = []
    for i in range(item_count):
        p = rnd.randint(1 , TOTAL_POSSIBLY)
        for j in range(len(ITEMS)):
            if p <= ITEMS[j][0]:
                break
            p -= ITEMS[j][0]
        temp_items.append(ITEMS[j][1])
    if room.p1_state == P_HOLDING:
        for item in temp_items:
            if len(room.p1_items) == 8:
                break
            room.p1_items.append(item)
        if room.p2_state == P_LOCKED:
            room.p2_state = P_UNLOCKED
        else:
            room.p1_state = P_WAITING
            room.p2_state = P_HOLDING
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[神秘礼物]！抽到了两个随机道具：\n{temp_items[0].name}\n{temp_items[1].name}"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        for item in temp_items:
            if len(room.p2_items) == 8:
                break
            room.p2_items.append(item)
        if room.p1_state == P_LOCKED:
            room.p1_state = P_UNLOCKED
        else:
            room.p2_state = P_WAITING
            room.p1_state = P_HOLDING
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[神秘礼物]！抽到了两个随机道具：\n{temp_items[0].name}\n{temp_items[1].name}"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_magic_skin(bot : Bot , room : Room):
    TOTAL_POSSIBLY = 0
    for pair in ITEMS:
        TOTAL_POSSIBLY += pair[0]
    item_count = 2
    temp_items : list[Item] = []
    for i in range(item_count):
        p = rnd.randint(1 , TOTAL_POSSIBLY)
        for j in range(len(ITEMS)):
            if p <= ITEMS[j][0]:
                break
            p -= ITEMS[j][0]
        temp_items.append(ITEMS[j][1])
    if room.p1_state == P_HOLDING:
        if room.p1_HP >= room.max_hp[0]:
            room.p1_HP -= 1
        room.max_hp[0] -= 1
        for item in temp_items:
            if len(room.p1_items) == 8:
                break
            room.p1_items.append(item)
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[玄奇驴皮]！失去了一点生命和血上限，抽到了两个道具：\n{temp_items[0].name}\n{temp_items[1].name}"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        if room.p2_HP >= room.max_hp[1]:
            room.p2_HP -= 1
        room.max_hp[1] -= 1
        for item in temp_items:
            if len(room.p2_items) == 8:
                break
            room.p2_items.append(item)
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[玄奇驴皮]！失去了一点生命和血上限，抽到了两个道具：\n{temp_items[0].name}\n{temp_items[1].name}"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

async def f_baggy(bot : Bot , room : Room):
    def __p_Health_Up(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            room.max_hp[0] += 1
            room.p1_HP += 1
        else:
            room.max_hp[1] += 1
            room.p2_HP += 1
        return ("体力上升" , "获得了一点生命上限。")
    def __p_Health_Down(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            if room.max_hp[0] == 1:
                room.max_hp[0] += 1
                room.p1_HP += 1
                return ("体力上升？" , "获得了一点生命上限。")
            if room.p1_HP >= room.max_hp[0]:
                room.p1_HP -= 1
            room.max_hp[0] -= 1
        else:
            if room.max_hp[1] == 1:
                room.max_hp[1] += 1
                room.p2_HP += 1
                return ("体力上升？" , "获得了一点生命上限。")
            if room.p2_HP >= room.max_hp[1]:
                room.p2_HP -= 1
            room.max_hp[1] -= 1
        return ("体力下降" , "失去了一点生命上限。")
    def __p_Full_Health(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            if room.p1_HP < room.max_hp[0]:
                room.p1_HP = room.max_hp[0]
        else:
            if room.p2_HP < room.max_hp[1]:
                room.p2_HP = room.max_hp[1]
        return ("体力回满" , "恢复了所有生命值。")
    def __p_Bad_Trip(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            if room.p1_HP == 1:
                room.p1_HP = room.max_hp[0]
                return ("体力回满？" , "恢复了所有生命值。")
            room.p1_HP -= 1
        else:
            if room.p2_HP == 1:
                room.p2_HP = room.max_hp[1]
                return ("体力回满？" , "恢复了所有生命值。")
            room.p2_HP -= 1
        return ("过激幻觉" , "受到了一点伤害。")
    def __p_Balls_of_Steel(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            room.p1_HP += 2
        else:
            room.p2_HP += 2
        return ("钢铁双蛋" , "获得了两点生命值。")    
    def __p_Paralysis(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            room.p1_state = P_WAITING
            room.p2_state = P_HOLDING
        else:
            room.p1_state = P_HOLDING
            room.p2_state = P_WAITING
        return ("麻痹" , "跳过了自己的回合。")
    def __p_Hematemesis(room : Room) -> tuple[str , str]:
        if room.p1_state == P_HOLDING:
            if room.max_hp[0] == 1:
                room.p1_HP = 1
            else:
                room.p1_HP = 1 + rnd.randint(0 , room.max_hp[0] - 1)
            return ("呕血" , "血量被重置为了%d。"%(room.p1_HP))
        else:
            if room.max_hp[1] == 1:
                room.p2_HP = 1
            else:
                room.p2_HP = 1 + rnd.randint(0 , room.max_hp[1] - 1)
            return ("呕血" , "血量被重置为了%d。"%(room.p2_HP))
    pills = [
    __p_Health_Up,
    __p_Health_Down,
    __p_Full_Health,
    __p_Bad_Trip,
    __p_Balls_of_Steel,
    __p_Paralysis,
    __p_Hematemesis
    ]
    pill = rnd.choice(pills)
    if room.p1_state == P_HOLDING:
        ret = pill(room)
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[小药袋]！触发了药丸<{ret[0]}>的效果：\n{ret[1]}"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        ret = pill(room)
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[小药袋]！触发了药丸<{ret[0]}>的效果：\n{ret[1]}"
        await bot.send_group_msg(group_id = room.g_id , message = msg)

'''
async def f_item(bot : Bot , room : Room):
    if room.p1_state == P_HOLDING:
        # Build output Message
        msg = MessageSegment.at(room.p1_id)
        msg += f" 使用了道具[]！"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
    else:
        # Build output Message
        msg = MessageSegment.at(room.p2_id)
        msg += f" 使用了道具[]！"
        await bot.send_group_msg(group_id = room.g_id , message = msg)
'''

ITEMS : list[tuple[int , Item]] = [
    (30 , Item("香烟" , "使用时，恢复一点生命值。" , f_cigarette , "生命恢复")),
    (40 , Item("过期的药" , "使用时，有概率恢复两点生命值，有概率失去一点生命值。" , f_medicine , "概率生命恢复")),
    (60 , Item("手锯" , "使用时，下一次射击伤害加一。" , f_handsaw , "伤害上升")),
    (60 , Item("转换器" , "使用后，切换下一发子弹的类型。" , f_inverter , "转换命运")),
    (60 , Item("汽水" , "使用后能退一发子弹。" , f_beer , "弹药弹出")),
    (60 , Item("放大镜" , "使用时能查看下一发子弹的类型。" , f_magnifying_glass , "查看子弹")),
    (50 , Item("手铐" , "使用后，使对方下一回合无法行动。" , f_handcuffs , "跳过回合")),
    (20 , Item("神秘礼物" , "使用后，抽取两个道具。但是，代价是什么呢。" , f_gift , "为你精心包装！")),
    (20 , Item("小药袋" , "使用后，随机触发一种胶囊的效果。" , f_baggy , "随机胶囊")),
    (10 , Item("玄奇驴皮" , "使用后，血量下降，抽取两个道具。" , f_magic_skin , "满足你所有的愿望")),
    (15 , Item("D6" , "使用后，重置手里的所有道具。" , f_d6 , "重置你的命运")),
    (10 , Item("D100" , "使用后，重置你的生命值、剩下的道具和子弹。" , f_d100 , "重置一切!")),
    ]

ADMIN : list[int] = [24938120 , ]
COOL_DOWN = 1200
MAX_WAITING = 1800

rooms : dict[int , Room | int] = {}

roulette = on_command("roulette", aliases = {"r" , "~"} , force_whitespace = " ", priority=10, block=False)

@roulette.handle()
async def roulette_handle(bot : Bot , event : MessageEvent | GroupMessageEvent):
    rnd.seed(time.time())
    flag = False
    if isinstance(event , GroupMessageEvent):
        texts = event.get_plaintext().strip().split(" ")
        for i in range(len(texts)):
            texts[i] = texts[i].strip()
        if not flag:
            flag = await game_enter(bot , event , texts)
        if not flag:
            flag = await admin_input(event , bot , texts)
        if not flag:
            flag = await user_input(event , bot , texts)
        if not flag:
            flag = await player_input(event , bot , texts)
            if flag:
                await game_state(event , bot)
        if not flag:
            await roulette.finish("参数有误。")

async def game_enter(bot : Bot , event : GroupMessageEvent , texts : list[str]) -> bool:
    if len(texts) == 1:
        # Room has created.
        if event.group_id in rooms:
            # In Cool Down.
            if type(rooms[event.group_id]) == float and time.time() - rooms[event.group_id] < COOL_DOWN:
                delta_time = datetime.datetime.fromtimestamp(rooms[event.group_id] + COOL_DOWN) - datetime.datetime.now()
                msg = f"房间正在重整，请稍后再来...\n剩余时间：{delta_time.seconds // 60:0>2}:{delta_time.seconds % 60:0>2}。"
                await roulette.finish(group_id = event.group_id , message = msg)
            # Enter Room that is empty.
            if type(rooms[event.group_id]) is float:
                rooms[event.group_id] = Room(event.group_id)
                await rooms[event.group_id].p1_join(bot , event.get_user_id())
                return True
            # Enter Room with a person waiting.
            elif rooms[event.group_id].game_state == R_WAITING:
                # Not P1 Player enter.
                if event.get_user_id() != rooms[event.group_id].p1_id:
                    # Start the game.
                    await rooms[event.group_id].p2_join(bot , event.get_user_id())
                    rooms[event.group_id].g_start(bot)
                    await rooms[event.group_id].r_start(bot)
                    return True
                # P1 Player enter.
                else:
                    msg = f"你已经在房间里了！"
                    await roulette.finish(group_id = event.group_id , message = msg)
            # Enter Room that is started.
            elif rooms[event.group_id].game_state == R_RUNNING:
                msg = f"游戏已经开始了！"
                await roulette.finish(group_id = event.group_id , message = msg)
            return False
        # Room has not created.
        if event.group_id not in rooms:
            rooms[event.group_id] = Room(event.group_id)
            await rooms[event.group_id].p1_join(bot , event.get_user_id())
            return True
    if len(texts) == 2:
        if texts[1] in ("退出" , "离开"):
            if event.group_id in rooms and type(rooms[event.group_id]) == Room:
                if rooms[event.group_id].game_state == R_RUNNING:
                    if event.get_user_id() == rooms[event.group_id].p1_id or event.get_user_id() == rooms[event.group_id].p2_id:
                        roulette.finish("比赛已开始，不要临阵脱逃。")
                    else:
                        roulette.finish("你不在房间里。")
                if rooms[event.group_id].game_state == R_WAITING and event.get_user_id() == rooms[event.group_id].p1_id:
                    rooms[event.group_id] = 0.0
                    roulette.finish("已离开房间。")
                else:
                    roulette.finish("你不在房间里。")
    return False

async def admin_input(event : GroupMessageEvent , bot : Bot , texts : list[str]) -> bool:
    if int(event.get_user_id()) in ADMIN:
        if event.group_id in rooms:
            if len(texts) == 2 and texts[1] == "停止" and type(rooms[event.group_id]) == Room:
                rooms[event.group_id] = time.time()
                await roulette.finish("房间已停止。")
            if len(texts) == 2 and texts[1] == "重置" and type(rooms[event.group_id]) == float:
                rooms[event.group_id] = 0.0
                await roulette.finish("冷却已清除。")
    return False

async def user_input(event : GroupMessageEvent , bot : Bot , texts : list[str]) -> bool:
    # Help
    if len(texts) == 2 and (texts[1] == "帮助" or texts[1] == "help"):
        r = redis.StrictRedis(host = "127.0.0.1" , port = 6379 , db = 1)
        symbol = r.hget("g_symbols" , event.group_id)
        if symbol == None:
            symbol = "!"
        else:
            symbol = symbol.decode()[0]
        msg = f"可用指令（roulette可以用r或者~替换）：\n"
        msg += f"{DIVIDER}\n"
        msg += f"输入\"{symbol}roulette\"加入对局。\n"
        msg += f"输入\"{symbol}roulette 退出\"离开对局。\n"
        msg += f"{DIVIDER}\n"
        msg += f"游戏内指令：\n"
        msg += f"{symbol}roulette 开枪 自己\n"
        msg += f"{symbol}roulette 开枪 对方\n"
        msg += f"{symbol}roulette 使用 道具\n"
        msg += f"{symbol}roulette 查询\n"
        msg += f"{symbol}roulette 查询 道具\n"
        msg += f"{symbol}roulette 查看局势"
        await roulette.finish(group_id = event.group_id , message = msg)
    if len(texts) == 2 and texts[1] == "查询":
        msg = "道具列表：\n"
        for item in ITEMS:
            msg += f"{item[1].name}：{item[1].description}\n"
        await roulette.finish(msg.strip())
    if len(texts) == 3 and texts[1] == "查询":
        for item in ITEMS:
            if texts[2] == item[1].name:
                await roulette.finish(f"[{item[1].name}]\n{item[1].shortcut}\n作用：{item[1].description}")
        else:
            await roulette.finish("不存在这个道具。")
    if len(texts) == 2 and texts[1] == "查看局势":
        if type(rooms[event.group_id]) == Room:
            await rooms[event.group_id].r_check(bot)
            return True
    return False

async def player_input(event : GroupMessageEvent , bot : Bot , texts : list[str]) -> bool:
    if event.group_id in rooms and type(rooms[event.group_id]) == Room and rooms[event.group_id].game_state == R_RUNNING:
        room : Room = rooms[event.group_id]
        if room.r_is_turn(event.get_user_id()):
            if len(texts) == 3 and texts[1] in ("开枪" , "开火" , "射击") and texts[2] == "自己":
                if event.get_user_id() == room.p1_id:
                    await room.r_shoot(bot , 1)
                else:
                    await room.r_shoot(bot , 2)
                return True
            if len(texts) == 3 and texts[1] in ("开枪" , "开火" , "射击") and texts[2] in ("对方" , "对手" , "敌人"):
                if event.get_user_id() == room.p1_id:
                    await room.r_shoot(bot , 2)
                else:
                    await room.r_shoot(bot , 1)
                return True
            if len(texts) == 3 and texts[1] == "使用":
                await room.r_use_item(bot , texts[2])
                return True
        else:
            if len(texts) == 3 and texts[1] in ("开枪" , "开火" , "射击") and texts[2] == "自己":
                await roulette.finish("不是你的回合。")
            if len(texts) == 3 and texts[1] in ("开枪" , "开火" , "射击") and texts[2] in ("对方" , "对手" , "敌人"):
                await roulette.finish("不是你的回合。")
            if len(texts) == 3 and texts[1] == "使用":
                await roulette.finish("不是你的回合。")
    return False

async def game_state(event : GroupMessageEvent , bot : Bot):
    if event.group_id in rooms and type(rooms[event.group_id]) == Room and rooms[event.group_id].game_state == R_RUNNING:
        if rooms[event.group_id].r_is_end():
            room = rooms[event.group_id]
            rooms[event.group_id] = time.time()
            if room.p1_HP <= 0:
                await roulette.finish("比赛结束。获胜者" + MessageSegment.at(room.p2_id))
            else:
                await roulette.finish("比赛结束。获胜者" + MessageSegment.at(room.p1_id))
        if len(rooms[event.group_id].bullets) == 0:
            await rooms[event.group_id].r_start(bot)
        else:
            if rooms[event.group_id].p1_state == P_HOLDING:
                await roulette.finish("接下来是" + MessageSegment.at(rooms[event.group_id].p1_id) + " 的回合。")
            else:
                await roulette.finish("接下来是" + MessageSegment.at(rooms[event.group_id].p2_id) + " 的回合。")
#        else:
#            await rooms[event.group_id].r_check(bot)