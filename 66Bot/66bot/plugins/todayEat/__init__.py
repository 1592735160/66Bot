from typing import List

from nonebot import on_regex, require, on_command, logger
from nonebot.adapters.onebot.v11 import MessageEvent, Bot, GroupMessageEvent, MessageSegment, GROUP, GROUP_ADMIN, \
    GROUP_OWNER, Message
from nonebot.internal.matcher import Matcher
from nonebot.params import RegexMatched, CommandArg
from nonebot.permission import SUPERUSER
from .util import Meals, save_cq_image
from .data_source import eating_manager

todayEat_version__ = "v0.3.4"
todayEat_notes__ = f'''
今天吃什么？ {todayEat_version__}
[xx吃xx]    问bot吃什么
[xx喝xx]    问bot喝什么
[主食吃xx]   问bot吃什么主食
[主食添加 xx] 添加主食至群主食菜单
[添加 xx]   添加菜品至群菜单
[移除 xx]   从菜单移除菜品
[加菜 xx]   添加菜品至基础菜单
[菜单]        查看群菜单
[基础菜单] 查看基础菜单
[开启/关闭小助手] 开启/关闭吃饭小助手
[添加/删除问候 时段 问候语] 添加/删除吃饭小助手问候语'''.strip()

# 定时任务
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

what2eat = on_regex(r"^(今天|[早中下晚][上饭餐午]|早上|夜宵|今晚)吃(什么|啥|点啥)(帮助)?$", priority=15)
what2drink = on_regex(r"^(今天|[早中下晚][上饭餐午]|早上|夜宵|今晚)喝(什么|啥|点啥)(帮助)?$", priority=15)
today_eat_food = on_regex(r"^(主食)吃(什么|啥|点啥)(帮助)?$", priority=15)
group_add = on_command("添加",   priority=15, block=True)
group_food_add = on_command("添加主食", priority=15, block=True)
group_remove = on_command("移除",  priority=15, block=True)
basic_add = on_command("加菜", permission=SUPERUSER, priority=15, block=True)
show_basic_menu = on_command("基础菜单", permission=GROUP, priority=15, block=True)
show_group_menu = on_command("菜单", aliases={"群菜单", "查看菜单"}, permission=GROUP, priority=15, block=True)
show_group_food = on_command("主食菜单", aliases={"群主食菜单", "查看主食菜单"}, permission=GROUP, priority=15, block=True)
greeting_on = on_command("开启小助手", aliases={"启用小助手"}, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=12, block=True)
greeting_off = on_command("关闭小助手", aliases={"禁用小助手"}, permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER, priority=12, block=True)


@what2eat.handle()
async def _(event: MessageEvent, args: str = RegexMatched()):
    # if event.get_user_id() == '554694515':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你吃尼玛'))

    if args[-2:] == "帮助":
        await what2eat.finish(todayEat_notes__)

    msg = eating_manager.get2eat(event)
    await what2eat.finish(msg)

@today_eat_food.handle()
async def _(event: MessageEvent, args: str = RegexMatched()):
    # if event.get_user_id() == '554694515':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你吃尼玛'))

    if args[-2:] == "帮助":
        await what2eat.finish(todayEat_notes__)

    msg = eating_manager.todayEatFood(event)
    await what2eat.finish(msg)

@what2drink.handle()
async def _(event: MessageEvent, args: str = RegexMatched()):
    # if event.get_user_id() == '554694515':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你喝尼玛'))
    if args[-2:] == "帮助":
        await what2drink.finish(todayEat_notes__)
    if event.get_user_id() == '1604322672':
        await what2drink.finish("喝水吧马姐")
    msg = eating_manager.get2drink(event)
    await what2drink.finish(msg)

@show_basic_menu.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    is_too_many_lines, msg = eating_manager.show_basic_menu()
    if is_too_many_lines:
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=MessageSegment.node_custom(int(bot.self_id), list(bot.config.nickname)[0], msg))
    else:
        await matcher.finish(msg)

@greeting_on.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    eating_manager.update_groups_on(gid, True)
    await greeting_on.finish("已开启吃饭小助手~")

@greeting_off.handle()
async def _(event: GroupMessageEvent):
    gid = str(event.group_id)
    eating_manager.update_groups_on(gid, False)
    await greeting_off.finish("已关闭吃饭小助手~")


@group_add.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args_str: List[str] = args.extract_plain_text().strip().split()
    # if event.get_user_id() == '554694515':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你加尼玛'))
    # if event.get_user_id() == '3326279934':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你加尼玛'))
    if not args_str:
        await group_add.finish("还没输入你要添加的菜品呢~")
    elif len(args_str) > 1:
        await group_add.finish("添加菜品参数错误~")

    # If image included, save it, return the path in string
    await save_cq_image(args, eating_manager._img_dir)

    # Record the whole string, including the args after transfering
    msg: str = eating_manager.add_group_food(event, str(args))

    if "[CQ:image" in str(args):
        await group_add.finish(args.append(MessageSegment.text(" " + msg)))
    else:
        await group_add.finish(args.append(MessageSegment.text(msg)))

@group_food_add.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args_str: List[str] = args.extract_plain_text().strip().split()
    # if event.get_user_id() == '554694515':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你加尼玛'))
    # if event.get_user_id() == '3326279934':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你加尼玛'))
    if not args_str:
        await group_add.finish("还没输入你要添加的菜品呢~")
    elif len(args_str) > 1:
        await group_add.finish("添加菜品参数错误~")

    # If image included, save it, return the path in string
    await save_cq_image(args, eating_manager._img_dir)

    # Record the whole string, including the args after transfering
    msg: str = eating_manager.add_food_group(event, str(args))

    if "[CQ:image" in str(args):
        await group_add.finish(args.append(MessageSegment.text(" " + msg)))
    else:
        await group_add.finish(args.append(MessageSegment.text(msg)))

@group_remove.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    args: List[str] = args.extract_plain_text().strip().split()
    # if event.get_user_id() == '3326279934':
    #     await group_add.finish(
    #         Message(f'[CQ:at,qq={event.get_user_id()}] 你移尼玛'))
    if not args:
        await group_remove.finish("还没输入你要移除的菜品呢~")
    elif len(args) > 1:
        await group_remove.finish("移除菜品参数错误~")

    msg: MessageSegment = eating_manager.remove_food(event, args[0])

    await group_remove.finish(MessageSegment.text(msg))

@show_group_menu.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    is_too_many_lines, msg = eating_manager.show_group_menu(gid)
    if is_too_many_lines:
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=[MessageSegment.node_custom(int(bot.self_id), list(bot.config.nickname)[0], str(msg))])
    else:
        await matcher.finish(msg)

@show_group_food.handle()
async def _(bot: Bot, matcher: Matcher, event: GroupMessageEvent):
    gid = str(event.group_id)
    is_too_many_lines, msg = eating_manager.show_group_food(gid)
    if is_too_many_lines:
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=[MessageSegment.node_custom(int(bot.self_id), list(bot.config.nickname)[0], str(msg))])
    else:
        await bot.call_api("send_group_forward_msg", group_id=event.group_id, messages=[MessageSegment.node_custom(int(bot.self_id), list(bot.config.nickname)[0], str(msg))])


@basic_add.handle()
async def _(args: Message = CommandArg()):

    args_str: List[str] = args.extract_plain_text().strip().split()
    if not args_str:
        await basic_add.finish("还没输入你要添加的菜品呢~")
    elif len(args_str) > 1:
        await group_add.finish("添加菜品参数错误~")

    # The same as above
    await save_cq_image(args, eating_manager._img_dir)
    msg: str = eating_manager.add_basic_food(str(args))

    if "[CQ:image" in str(args):
        await group_add.finish(args.append(MessageSegment.text(" " + msg)))
    else:
        await group_add.finish(args.append(MessageSegment.text(msg)))


# ------------------------- Schedulers -------------------------
# 重置吃什么次数，包括夜宵
@scheduler.scheduled_job("cron", hour="6,11,17,22", minute=0, misfire_grace_time=60)
async def _():
    eating_manager.reset_count()
    logger.info("今天吃什么次数已刷新")

# 早餐提醒
@scheduler.scheduled_job("cron", hour=9, minute=20, misfire_grace_time=60)
async def time_for_breakfast():
    await eating_manager.do_greeting(Meals.BREAKFAST)
    logger.info(f"已群发早餐提醒")

# 午餐提醒
@scheduler.scheduled_job("cron", hour=11, minute=0, misfire_grace_time=60)
async def time_for_lunch():
    await eating_manager.do_greeting(Meals.LUNCH)
    logger.info(f"已群发午餐提醒")

# 下午茶/摸鱼提醒
@scheduler.scheduled_job("cron", hour=15, minute=0, misfire_grace_time=60)
async def time_for_snack():
    await eating_manager.do_greeting(Meals.SNACK)
    logger.info(f"已群发摸鱼提醒")

# 六六下班用
@scheduler.scheduled_job("cron",hour=17, minute=20,misfire_grace_time=60)
async def time_for_demo():
    await eating_manager.do_greeting(Meals.SIXSIX)
    logger.info(f"已群发六六暗示")

# 晚餐提醒
@scheduler.scheduled_job("cron", hour=18, minute=0, misfire_grace_time=60)
async def time_for_dinner():
    await eating_manager.do_greeting(Meals.DINNER)
    logger.info(f"已群发晚餐提醒")

#六六打游戏用
@scheduler.scheduled_job("cron",hour=20, minute=0,misfire_grace_time=60)
async def time_for_demo():
    await eating_manager.do_greeting(Meals.PLAY)
    logger.info(f"已群发六六暗示")

# 夜宵提醒
@scheduler.scheduled_job("cron", hour=22, minute=0, misfire_grace_time=60)
async def time_for_midnight():
    await eating_manager.do_greeting(Meals.MIDNIGHT)
    logger.info(f"已群发夜宵提醒")

