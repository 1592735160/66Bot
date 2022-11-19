from datetime import date
from pathlib import Path

import nonebot
import random
from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Event, Message
from nonebot.plugin import on_keyword

from .config import Config

global_config = get_driver().config
config = Config.parse_obj(global_config)

# Export something for other plugin
# export = nonebot.export()
# export.foo = "bar"

# @export.xxx
# def some_function():
#     pass

_sub_plugins = set()
_sub_plugins |= nonebot.load_plugins(
    str((Path(__file__).parent / "plugins").
    resolve()))


def luck_simple(num):
    if num <= 1:
        return '大大大大吉'
    elif num < 10:
        return '走了陈三屎运的大吉'
    elif num == 13:
        return '你在s13一定能夺冠把  因为你就是s13'
    elif num < 18:
        return '大吉'
    elif num == 30:
        return '人品都能抽到30  你和陈30一样霉逼'
    elif num == 50:
        return '半凶半吉 今天补刀指定补一半漏一半'
    elif num < 53:
        return '吉'
    elif num < 58:
        return '半吉'
    elif num < 62:
        return '小吉'
    elif num < 65:
        return '末小吉'
    elif num < 71:
        return '末吉'
    elif num < 80:
        return '小霉逼 离我远点'
    elif num == 88:
        return '今年一定发发发发'
    elif num < 90:
        return '大霉逼 离我远点'
    elif num < 100:
        return '凶'
    else:
        return '大大大大大凶'


jrrp = on_keyword(['jrrp', '今日人品'])
# fen = on_keyword(['男朋友', '女朋友', 'npy', '老公', '老婆', '对象'])


@jrrp.handle()
async def jrrp_handle(bot: Bot, event: Event):
    rnd = random.Random()
    rnd.seed(int(date.today().strftime("%y%m%d")) + int(event.get_user_id()))
    lucknum = rnd.randint(1, 100)
    if(event.get_user_id()=='15927351601'):
        lucknum = 1
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}/100（越低越好），为"{luck_simple(lucknum)}"'))
    # elif(event.get_user_id()=='3516545723'):
    #     lucknum = 100
    #     await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}/100（越低越好），为"{luck_simple(lucknum)}，建议给66一个管理员，为你逢凶化吉"'))
    # elif(event.get_user_id() =='554694515'):
    #     await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}] 你占尼玛'))
    elif(event.get_user_id() == '1969468803'):
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}/100（越低越好），为"{luck_simple(lucknum)}"，祝你福如东海,寿比南山'))
    else:
        await jrrp.finish(Message(f'[CQ:at,qq={event.get_user_id()}]您今日的幸运指数是{lucknum}/100（越低越好），为"{luck_simple(lucknum)}"'))

@jrrp.handle()
async def jrrp_handle():
    pass

# @fen.handle()
# async def fen_handle(bot: Bot, event: Event):
#     await jrrp.finish(Message(f'[CQ:reply,id={str(event.message_id)}]分手'))
#
# @fen.handle()
# async def fen_handle():
#     pass




