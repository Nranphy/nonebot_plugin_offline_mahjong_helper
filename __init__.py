from nonebot.plugin import PluginMetadata


__plugin_meta__ = PluginMetadata(
    name = '此乃面麻小助手！！',
    description="面麻小插件...来成为现充吧！！",
    usage='''
【/雀魂查询 xxx】按照指示对指定名称用户进行查询
===
约桌相关指令请用【/约桌帮助】
===
【/精算 xxxxx xxxxx xxxxx xxxxx】根据雀魂规则进行精算，xxxxx为每家分数
【/算分 xx x】对传入的番数和符数查表算点数，两者顺序任意
===
【/雀魂查询 xxx】对指定用户名查询雀魂战绩
''',
    extra={
        "author": "Nranphy",
        "version": "0.2.2",
        "repository": "https://github.com/Nranphy/nonebot_plugin_offline_mahjong_helper",
        "visible": True,
        "default_enable": True
    }
)


# 预约相关
from .appoint import *

# 计算相关
from .count import *

# 查询相关
from .query import *