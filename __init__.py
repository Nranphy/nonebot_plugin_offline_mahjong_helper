from nonebot import on_command, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.params import State
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger


__kirico_plugin_name__ = '面麻小助手'

__kirico_plugin_author__ = 'Nranphy'

__kirico_plugin_version__ = '0.1.0'

__kirico_plugin_repositorie__ = ''

__kirico_plugin_description__ = ''

__kirico_plugin_usage__ = '''【/雀魂查询 xxx】按照指示对指定名称用户进行查询
=========
约桌相关
【/约桌】可查看约桌表格，进行约桌
【/所有牌桌】查看所有群预约的牌桌
【/我的牌桌】可查看与自己有关的所有牌桌
【/牌桌细节 xxxxx】可查看牌桌的所有细节
【/牌桌查询】可查询指定条件牌桌，请直接输入查看具体指示
【/加入牌桌 xxxxx】加入指定编号的牌桌
【/退出牌桌 xxxxx】同上，注意最后一人退出牌桌会导致牌桌解散
【/解散牌桌 xxxxx】可以解散自己创建的牌桌
=========
计算相关
【/精算 xxx xxx xxx xxx】以雀魂标准进行点数精算√
【/算点 xx xx】进行查表算点数（ppss.两个参数为符和番数，不用考虑顺序）'''

__kirico__plugin_visible__ = True




from .appoint import *
from .count import *
from .query import *

