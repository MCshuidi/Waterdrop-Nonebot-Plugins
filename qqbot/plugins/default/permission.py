from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.matcher import Matcher
from nonebot.exception import IgnoredException
from nonebot.message import run_preprocessor

import redis

DEBUG = True

@run_preprocessor
async def permission_test(bot : Bot , matcher : Matcher , event : MessageEvent | GroupMessageEvent):
    if event.get_plaintext().strip() == "":
        if DEBUG:print("Empty input.")
        raise IgnoredException("Empty input.")
    # Connect to database and get data
    r = redis.StrictRedis(host = "127.0.0.1", port = 6379, db = 1)
    # Global Whitelist test
    if isinstance(event , GroupMessageEvent):
        uid_whitelist = event.group_id
        uid_symbol = event.group_id
        if DEBUG:print(uid_whitelist)
        if DEBUG:print(list(matcher.rule.checkers)[0].call.cmds)
        # Whitelist test
        for cmd in list(matcher.rule.checkers)[0].call.cmds:
            g_status = r.hget("global_whitelist" , cmd[0])
            if g_status is not None:
                if g_status.decode() == '+' or g_status.decode() == '*':
                    break
                if g_status.decode() == '-':
                    if DEBUG:print("Do not pass global whitelist.")
                    raise IgnoredException("Do not pass global whitelist.")
                if g_status.decode()[0] == "=":
                    g2_status = r.hget("global_whitelist" , g_status.decode()[1:])
                    if g2_status.decode() == '+' or g2_status.decode() == '*':
                        break
                    if g2_status.decode() == '-':
                        if DEBUG:print("Do not pass global whitelist.")
                        raise IgnoredException("Do not pass global whitelist.")
        else:
            if DEBUG:print("Do not pass base whitelist.")
            raise IgnoredException("Do not pass base whitelist.")
        status = r.hget("g_%d"%(uid_whitelist) , "exists")
        if status is None or status.decode() == '-':
            if DEBUG:print("Do not pass whitelist.")
            raise IgnoredException("Do not pass whitelist.")
        if g_status[0] == "=":
            t_status = r.hget("g_%d"%(uid_whitelist) , g_status[1:])
            if g2_status.decode() == '*':
                if not (t_status is not None and t_status.decode() == "+"):
                    if DEBUG:print("Do not pass whitelist.[=*]")
                    raise IgnoredException("Do not pass whitelist.[=*]")
            elif g2_status.decode() == '+':
                if t_status is not None and t_status.decode() == "-":
                    if DEBUG:print("Do not pass whitelist.[=+]")
                    raise IgnoredException("Do not pass whitelist.[=+]")
        elif g_status.decode() == '*':
            for cmd in list(matcher.rule.checkers)[0].call.cmds:
                status = r.hget("g_%d"%(uid_whitelist) , cmd[0])
                if status is not None and status.decode() == "+":
                    break
            else:
                if DEBUG:print("Do not pass whitelist.[*]")
                raise IgnoredException("Do not pass whitelist.[*]")
        elif g_status.decode() == '+':
            for cmd in list(matcher.rule.checkers)[0].call.cmds:
                status = r.hget("g_%d"%(uid_whitelist) , cmd[0])
                if status is not None and status.decode() == "-":
                    if DEBUG:print("Do not pass whitelist.[+]")
                    raise IgnoredException("Do not pass whitelist.[+]")
        # Symbol test
        allowed_symbol = r.hget("g_symbols" , uid_symbol)
        if allowed_symbol is None:
            allowed_symbol = "!！"
        else:
            allowed_symbol = allowed_symbol.decode()
        if event.get_plaintext()[0] not in allowed_symbol:
            if DEBUG:print("The opening symbols do not match.")
            raise IgnoredException("The opening symbols do not match.")
    else:
        uid_whitelist = event.user_id
        uid_symbol = event.user_id
        # Whitelist test
        for cmd in list(matcher.rule.checkers)[0].call.cmds:
            g_status = r.hget("global_whitelist" , cmd[0])
            if g_status is not None:
                if g_status.decode() == '+' or g_status.decode() == '*':
                    break
                if g_status.decode() == '-':
                    if DEBUG:print("Do not pass global whitelist.")
                    raise IgnoredException("Do not pass global whitelist.")
                if g_status.decode()[0] == "=":
                    g2_status = r.hget("global_whitelist" , g_status.decode()[1:])
                    if g2_status.decode() == '+' or g2_status.decode() == '*':
                        break
                    if g2_status.decode() == '-':
                        if DEBUG:print("Do not pass global whitelist.")
                        raise IgnoredException("Do not pass global whitelist.")
        else:
            if DEBUG:print("Do not pass base whitelist.")
            raise IgnoredException("Do not pass base whitelist.")
        status = r.hget("u_%d"%(uid_whitelist) , "exists")
        if status is None or status.decode() == '-':
            if DEBUG:print("Do not pass whitelist.")
            raise IgnoredException("Do not pass whitelist.")
        if g_status[0] == "=":
            t_status = r.hget("g_%d"%(uid_whitelist) , g_status[1:])
            if g2_status.decode() == '*':
                if not (t_status is not None and t_status.decode() == "+"):
                    if DEBUG:print("Do not pass whitelist.[=*]")
                    raise IgnoredException("Do not pass whitelist.[=*]")
            elif g2_status.decode() == '+':
                if t_status is not None and t_status.decode() == "-":
                    if DEBUG:print("Do not pass whitelist.[=+]")
                    raise IgnoredException("Do not pass whitelist.[=+]")
        if g_status.decode() == '*':
            for cmd in list(matcher.rule.checkers)[0].call.cmds:
                status = r.hget("u_%d"%(uid_whitelist) , cmd[0])
                if status is not None and status.decode() == "+":
                    break
            else:
                if DEBUG:print("Do not pass whitelist.[*]")
                raise IgnoredException("Do not pass whitelist.[*]")
        elif g_status.decode() == '+':
            for cmd in list(matcher.rule.checkers)[0].call.cmds:
                status = r.hget("u_%d"%(uid_whitelist) , cmd[0])
                if status is not None and status.decode() == "-":
                    if DEBUG:print("Do not pass whitelist.[+]")
                    raise IgnoredException("Do not pass whitelist.[+]")
        # Symbol test
        allowed_symbol = r.hget("u_symbols" , uid_symbol)
        if allowed_symbol is None:
            allowed_symbol = "!！"
        else:
            allowed_symbol = allowed_symbol.decode() 
        if event.get_plaintext()[0] not in allowed_symbol:
            if DEBUG:print("The opening symbols do not match.")
            raise IgnoredException("The opening symbols do not match.")
    # OP Level test
    op_level = r.hget("op_level" , event.get_user_id())
    func_level = r.hget("func_level" , event.get_plaintext().split(" ")[0][1:])
    if func_level is None:
        func_level = 0
    else:
        func_level = int(func_level.decode())
    if op_level is None:
        op_level = 0
    else:
        op_level = int(op_level.decode())
    if op_level < func_level:
        if isinstance(event , GroupMessageEvent):
            await bot.send_group_msg(group_id = event.group_id , message = "Permission denied.")
        else:
            await bot.send_private_msg(user_id = event.get_user_id() , message = "Permission denied.")
        raise IgnoredException("Permission denied.")