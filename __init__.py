from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import State
from nonebot.adapters.onebot.v11 import Bot, Event


__kirico_plugin_name__ = '此乃面麻小助手！！'

__kirico_plugin_author__ = 'Nranphy'

__kirico_plugin_version__ = '0.0.10'

__kirico_plugin_repositorie__ = ''

__kirico_plugin_description__ = '某面麻小插件...来成为现充吧！！'

__kirico_plugin_usage__ = '''【/雀魂查询 xxx】按照指示对指定名称用户进行查询
=========
约桌相关指令请用【/约桌帮助】
======
【/精算 xxxxx xxxxx xxxxx xxxxx】根据雀魂规则进行精算，xxxxx为每家分数
【/算分 xx x】对传入的番数和符数查表算点数，两者顺序任意
======
【/雀魂查询 xxx】对指定用户名查询雀魂战绩'''

__kirico__plugin_visible__ = True




from .appoint import *

from .count import *

from .query import *