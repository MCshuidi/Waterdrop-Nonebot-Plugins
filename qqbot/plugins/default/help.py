from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import redis

help_cmd = on_command("help", force_whitespace = " ", priority=10, block=False)

@help_cmd.handle()
async def help_handle(event : MessageEvent | GroupMessageEvent):
    texts = event.get_plaintext().split(" ")
    if isinstance(event , GroupMessageEvent):
        uid_whitelist = "g_%d"%(event.group_id)
    else:
        uid_whitelist = "u_%d"%(event.user_id)
    r = redis.StrictRedis(host = "127.0.0.1" , port = 6379 , db = 1)
    # Access to all available commands.
    if len(texts) == 1:
        helps = r.hgetall("help_description")
        help_cmds = []
        for key in helps.keys():
            g_status = r.hget("global_whitelist" , key.decode())
            status = r.hget(uid_whitelist , key.decode())
            if g_status is not None and g_status.decode() == '+' and (status is None or status.decode() == '+'):
                help_cmds.append((key.decode() , r.hget("help_description" , key.decode()).decode()))
            elif g_status is not None and g_status.decode() == '*' and status is not None and status.decode() == '+':
                help_cmds.append((key.decode() , r.hget("help_description" , key.decode()).decode()))
            elif g_status is not None and g_status.decode()[0] == '=':
                g2_status = r.hget("global_whitelist" , g_status.decode()[1:])
                if g2_status is None or g2_status == '-':
                    continue
                status = r.hget(uid_whitelist , g_status.decode()[1:])
                if g2_status is not None and g2_status.decode() == '+' and (status is None or status.decode() == '+'):
                    help_cmds.append((key.decode() , r.hget("help_description" , key.decode()).decode()))
                elif g2_status is not None and g2_status.decode() == '*' and status is not None and status.decode() == '+':
                    help_cmds.append((key.decode() , r.hget("help_description" , key.decode()).decode()))
        help_cmds = sorted(help_cmds , key = lambda item : item[0])
        msg = "可用指令 :\n"
        for cmd in help_cmds:
            msg += "%s：%s\n"%(cmd[0] , cmd[1])
        await help_cmd.finish(msg.strip())
    if len(texts) == 2:
        g_status = r.hget("global_whitelist" , texts[1])
        status = r.hget(uid_whitelist , texts[1])   
        if r.hget("help_usage" , texts[1]) is None:
            await help_cmd.finish("Command description not found!")
        if g_status is not None and g_status.decode() == '+' and (status is not None and status.decode() == '-'):
            await help_cmd.finish("Permission denied.[+]")
        if g_status is not None and g_status.decode() == '*' and status is not None and status.decode() != '+':
            await help_cmd.finish("Permission denied.[*]")
        elif g_status is not None and g_status.decode()[0] == '=':
            g2_status = r.hget("global_whitelist" , g_status.decode()[1:])
            if g2_status is None or g2_status == '-':
                await help_cmd.finish("Permission denied.[=]")
            status = r.hget(uid_whitelist , g_status.decode()[1:])
            if   g2_status is not None and g2_status.decode() == '+' and not (status is None or status.decode() == '+'):
                await help_cmd.finish("Permission denied.[=+]")
            elif g2_status is not None and g2_status.decode() == '*' and not (status is not None and status.decode() == '+'):
                await help_cmd.finish("Permission denied.[=*]")
        perfix = r.hget("g_symbols" , event.group_id)
        if perfix is None:
            perfix = "!"
        else:
            perfix = perfix.decode()[0]
        ret_str = "%s ： %s \n用法 : %s%s"%(texts[1] , r.hget("help_description" , texts[1]).decode() , perfix , r.hget("help_usage" , texts[1]).decode())
        await help_cmd.finish(ret_str.strip())