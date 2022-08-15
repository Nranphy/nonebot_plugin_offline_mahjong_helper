'''约桌功能所需要的一些定时操作'''

from nonebot import get_bot, get_driver, require
from nonebot.log import logger
from .utils import at_all_joiner, valid_path, delete_table, get_joiner_number, get_now_date, read_table


try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception as e:
    logger.error("[面麻助手] require定时插件时出错，请检查插件加载顺序。若依然不能解决，请修改__init__.py此处并查看错误原因。")


async def check_table_everyday():
    '''每天定时at提醒当天牌局并删除过期牌局'''
    now_date = get_now_date()
    bot = get_bot()
    for path in valid_path.iterdir():
        temp_info = read_table(path)
        if now_date > temp_info["date"]:
            delete_table(path)
        if now_date == temp_info["date"]:
            number = len(temp_info['qqs'])
            the_remind = f"\n=========\n当前约桌人数仅为{number}人..." if number<4 else ''
            try:
                await bot.call_api("send_group_msg", group_id=temp_info["group"], message=at_all_joiner(path)+f"您有今天的约桌，请提前做好时间安排，与同桌群友保持联系。\n\
=========\n【牌桌信息】\n【地点】{temp_info['place']}\n【开始时间】{temp_info['start']}\n【结束时间】{temp_info['end']}\n【备注】{temp_info['notes']}"+the_remind)
            except:
                continue


time_list = get_driver().config.offline_mahjong_remind_time if hasattr(get_driver().config, "offline_mahjong_remind_time") else list()

try:
    for index, single_time in enumerate(time_list):
        scheduler.add_job(check_table_everyday, "cron", hour=single_time["HOUR"], minute=single_time["MINUTE"], id=f"mahjong_appoint_check_{single_time['HOUR']}")
        logger.info(f"[面麻助手] 新建计划任务成功！！  id:mahjong_appoint_check_{single_time['HOUR']},时间为{single_time['HOUR']}时{single_time['MINUTE']}分.")
except TypeError:
    logger.error("[面麻助手] 插件定时发送相关设置有误，请检查.env.*文件。")

logger.info("[面麻助手] 每日牌桌检查已定时完成√")