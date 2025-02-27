from nonebot import *
from nonebot.rule import *
from nonebot.internal.adapter import *
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent, MessageSegment

import time
import datetime
import psutil

ST_TIME = datetime.datetime.now()
OFFIST = datetime.timedelta(hours = 0)

status = on_command("status" , force_whitespace = "", priority=10, block=False)

@status.handle()
async def status_handle(event : MessageEvent | GroupMessageEvent):
    now_time = datetime.datetime.now()
    time_s = "当前时间：%s\n服务器已运行时长：%s\nBot已运行时长：%s"%(str(now_time + OFFIST).split(".")[0], str(now_time - datetime.datetime.fromtimestamp(psutil.boot_time())).split(".")[0], str(now_time - ST_TIME).split(".")[0])
    cpu_s = "cpu使用率：%s"%((str(psutil.cpu_percent(1))) + '%')
    free = str(round(psutil.virtual_memory().free / (1024.0 * 1024.0 * 1024.0), 2))
    total = str(round(psutil.virtual_memory().total / (1024.0 * 1024.0 * 1024.0), 2))
    memory = round(int(psutil.virtual_memory().total - psutil.virtual_memory().free) / float(psutil.virtual_memory().total) , 6)
    mem_s = "物理内存：%s GB\n剩余物理内存： %s GB\n物理内存使用率： %.2f %%"%(total , free , memory * 100)
    net = psutil.net_io_counters()
    bytes_sent = '{0:.2f} Mb'.format(net.bytes_recv / 1024 / 1024)
    bytes_rcvd = '{0:.2f} Mb'.format(net.bytes_sent / 1024 / 1024)
    net_s = "网卡接收数据：%s\n网卡发送数据：%s" % (bytes_rcvd, bytes_sent)
    await status.finish("水滴伯特|状态：运行中\n========================\n%s\n%s\n%s\n%s"%(time_s ,cpu_s ,mem_s ,net_s))