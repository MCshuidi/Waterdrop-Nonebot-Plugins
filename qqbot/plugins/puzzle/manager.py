from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.bot import Bot

from ..default.api import strawberryapi

import redis
import json
import os

BOT_ID = 1280785468

puzzle_list     = on_command("puzzle"       , force_whitespace = " " , priority = 10 , block = False)
puzzle_answer   = on_command("password"     , force_whitespace = " " , priority = 10 , block = False)
puzzle_release  = on_command("release_hint" , force_whitespace = " " , priority = 10 , block = False)
puzzle_hint     = on_command("hint"         , force_whitespace = " " , priority = 10 , block = False)
puzzle_solution = on_command("solution"     , force_whitespace = " " , priority = 10 , block = False)

@puzzle_list.handle()
async def puzzle_list_handle(bot : Bot , message : GroupMessageEvent):
    root = os.path.join(os.path.dirname(__file__) , "puzzles")
    puzzles = os.listdir(root)
    texts = []
    for puzzle in puzzles:
        puzzle_obj = json.loads(open(os.path.join(root , puzzle , "cfg.json")).read())
        if puzzle_obj["Public"]:
            if puzzle_obj["Solved"]:
                title = "[已解决]"
            else:
                title = "[未解决]"
            title += puzzle_obj["Title"]
            text = MessageSegment.text("%s\n出题者：%s | 草莓奖励：%d\n"%(title , puzzle_obj["Author"] , puzzle_obj["Reward"]))
            for image in puzzle_obj["Images"]:
                text += MessageSegment.image(os.path.join(root , puzzle , image))
            text += "\n"
            text += puzzle_obj["Question"]
            texts.append(MessageSegment.node_custom(BOT_ID , "谜题" , text))
    if len(texts) == 0:
        msg = MessageSegment.node_custom(BOT_ID , "谜题列表" , "现在还没有题目，请稍后再来吧。")
    else:
        msg = MessageSegment.node_custom(BOT_ID , "谜题列表" , texts[0])
        for text in texts[1:]:
            msg += MessageSegment.node_custom(BOT_ID , "谜题列表" , text)
    await puzzle_list.finish(msg)

@puzzle_answer.handle()
async def puzzle_answer_handle(bot : Bot , message : GroupMessageEvent):
    answer = " ".join(message.get_plaintext().split(" ")[1:])
    root = os.path.join(os.path.dirname(__file__) , "puzzles")
    puzzles = os.listdir(root)
    for puzzle in puzzles:
        puzzle_obj = json.loads(open(os.path.join(root , puzzle , "cfg.json")).read())
        if puzzle_obj["Public"]:
            if puzzle_obj["Answer"] == answer:
                if puzzle_obj["Solved"]:
                    if puzzle_obj["Solved_ID"] == int(message.get_user_id()):
                        await puzzle_answer.finish(MessageSegment.at(message.get_user_id()) + " 你已经答出来这个问题了哦。")
                    else:
                        await puzzle_answer.finish(MessageSegment.at(message.get_user_id()) + " 这道题已经被解出来了哦。")
                else:
                    if puzzle_obj["Author_ID"] == int(message.get_user_id()):
                        puzzle_answer.finish("你要干什么，你要自己答自己出的题？")
                    else:
                        puzzle_obj["Solved"] = True
                        puzzle_obj["Solved_ID"] = int(message.get_user_id())
                        open(os.path.join(root , puzzle , "cfg.json") , mode = "w" , encoding = "utf-8").write(json.dumps(puzzle_obj , indent = 4))
                        await strawberryapi.berrychange_api(bot , int(message.get_user_id()) , puzzle_obj["Reward"])
                        if puzzle_obj["Author_ID"] != -1:
                            await strawberryapi.berrychange_api(puzzle_obj["Author_ID"] , int(puzzle_obj["Reward"] * 0.6))
                            await puzzle_answer.finish(MessageSegment.at(message.get_user_id()) + " 密码正确，已经向回答者发送了 %d 个草莓。\n已经向出题者"%(puzzle_obj["Reward"]) + MessageSegment.at(puzzle_obj["Author_ID"]) + "发送了 %d 个草莓。"%(int(puzzle_obj["Reward"] * 0.6)))
                        else:
                            await puzzle_answer.finish(MessageSegment.at(message.get_user_id()) + " 密码正确，已经向回答者发送了 %d 个草莓。"%(puzzle_obj["Reward"]))
    else:
        await puzzle_answer.finish(MessageSegment.at(message.get_user_id()) + " 密码错误，没有任何反应！")

@puzzle_release.handle()
async def puzzle_release_handle(bot : Bot , message : GroupMessageEvent):
    release = " ".join(message.get_plaintext().split(" ")[1:])
    root = os.path.join(os.path.dirname(__file__) , "puzzles")
    puzzles = os.listdir(root)
    for puzzle in puzzles:
        puzzle_obj = json.loads(open(os.path.join(root , puzzle , "cfg.json")).read())
        if puzzle_obj["Public"]:
            if puzzle_obj["Title"] == release:
                if puzzle_obj["Released_Hints"] < len(puzzle_obj["Hints"]):
                    puzzle_obj["Released_Hints"] += 1
                    open(os.path.join(root , puzzle , "cfg.json") , mode = "w" , encoding = "utf-8").write(json.dumps(puzzle_obj , indent = 4))
                    if puzzle_obj["Released_Hints"] <= len(puzzle_obj["Hint_Titles"]):
                        title = f"：{puzzle_obj["Hint_Titles"][puzzle_obj["Released_Hints"] - 1]}"
                    else:
                        title = "："
                    await puzzle_release.finish(f"已解锁Puzzle \"{puzzle_obj["Title"]}\"的提示{puzzle_obj["Released_Hints"]:2}/{len(puzzle_obj["Hints"]):2}{title}\n提示内容：{puzzle_obj["Hints"][puzzle_obj["Released_Hints"] - 1]}")
                else:
                    await puzzle_release.finish(f"Puzzle \"{puzzle_obj["Title"]}\"的提示已全部解锁完毕！")
    else:
        await puzzle_hint.finish(f"不存在该Puzzle！请检查输入后再操作。")

@puzzle_hint.handle()
async def puzzle_hint_handle(bot : Bot , message : GroupMessageEvent):
    hints = " ".join(message.get_plaintext().split(" ")[1:])
    root = os.path.join(os.path.dirname(__file__) , "puzzles")
    puzzles = os.listdir(root)
    for puzzle in puzzles:
        puzzle_obj = json.loads(open(os.path.join(root , puzzle , "cfg.json")).read())
        if puzzle_obj["Public"]:
            if puzzle_obj["Title"] == hints:
                if len(puzzle_obj["Hints"]) == 0:
                    await puzzle_hint.finish("该Puzzle没有Hint。")
                msg = []
                for i in range(len(puzzle_obj["Hints"])):
                    if i < len(puzzle_obj["Hint_Titles"]):
                        title = f"{puzzle_obj["Hint_Titles"][i]}"
                    else:
                        title = ""
                    if i < puzzle_obj["Released_Hints"] or puzzle_obj["Solved"]:
                        msg.append(f"Hint {i + 1:2}/{len(puzzle_obj["Hints"]):2}：{title}\n{puzzle_obj["Hints"][i]}")
                    else:
                        if title == "":title = "？？？"
                        msg.append(f"Hint {i + 1:2}/{len(puzzle_obj["Hints"]):2}：{title}（提示未解锁）")
                await puzzle_hint.finish("\n".join(msg))
    else:
        await puzzle_hint.finish(f"不存在该Puzzle！请检查输入后再操作。")

@puzzle_solution.handle()
async def puzzle_solution_handle(bot : Bot , message : GroupMessageEvent):
    solution = " ".join(message.get_plaintext().split(" ")[1:])
    root = os.path.join(os.path.dirname(__file__) , "puzzles")
    puzzles = os.listdir(root)
    for puzzle in puzzles:
        puzzle_obj = json.loads(open(os.path.join(root , puzzle , "cfg.json")).read())
        if puzzle_obj["Public"]:
            if puzzle_obj["Title"] == solution:
                if puzzle_obj["Solved"]:
                    await puzzle_solution.finish(puzzle_obj["Solution"])
                else:
                    await puzzle_solution.finish(f"Puzzle \"{solution}\" 还未被解出来！")
    else:
        await puzzle_hint.finish(f"不存在该Puzzle！请检查输入后再操作。")