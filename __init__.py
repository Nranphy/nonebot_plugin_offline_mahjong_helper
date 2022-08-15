from nonebot import on_command, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.params import State
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .appoint import *
from .count import *
from .query import *


__kirico_plugin_name__ = '此乃面麻小助手！！'

__kirico_plugin_author__ = 'Nranphy'

__kirico_plugin_version__ = '0.0.5'

__kirico_plugin_repositorie__ = ''

__kirico_plugin_description__ = '某半途而废的小插件...没有人会用了啦！！'

# __kirico_plugin_usage__ = '''
# 输入【/精算 xxx xxx xxx xxx】以雀魂标准进行点数精算√
# （ps.其中xxx均为终局点数，需要用空格隔开哦）
# 不方便查表？用【/算点 xx xx】进行查表算点数
# （ppss.两个参数为符和番数，不用在意顺序，雾子酱会处理好的√）
# '''

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
【/解散牌桌 xxxxx】可以解散自己创建的牌桌'''

__kirico__plugin_visible__ = True




actuarial_point = on_command("计分", aliases={"精算","精算点"}, priority=10,block=True)

han_fu_2_point = on_command("算点",aliases={"算分"} ,priority=10,block=True)


# 将符和番输入得到点数
@han_fu_2_point.handle()
async def parse1(bot:Bot, event:Event, state:T_State = State()):
    msg = str(event.get_message()).split()
    try:
        state["han"] = min(int(msg[1]),int(msg[2]))
        state["fu"] = max(int(msg[1]),int(msg[2]))
    except Exception:
        await han_fu_2_point.finish("\n番、符输入格式有误×\n请检查是否用空格分隔指令。\n例：/算点 4 40", at_sender = True)

@han_fu_2_point.handle()
async def han_fu_2_point_action(bot:Bot, event:Event, state:T_State = State()):
    temp = point_counter(state["fu"], state["han"])
    if temp[0]:
        msg = f"\n点数计算成功√\n==={temp[3]}===\n【亲家和牌】荣和 {temp[1][0]} ，自摸 {temp[1][1]} \n【子家和牌】荣和 {temp[2][0]} ，自摸 {temp[2][1]} \n===计算完成~==="
    else:
        msg = f"\n点数计算成功√\n===查表失败===\n或因为指定符番组合不存在。\n已按计算规则进行计算：\n【亲家得点】 {temp[1]}\n【子家得点】 {temp[2]}\n===计算完成~==="
    await han_fu_2_point.finish(msg , at_sender = True)



# 精算点计算
@actuarial_point.handle()
async def parse2(bot:Bot, event:Event, state:T_State = State()):
    try:
        temp = str(event.get_message()).split()[1:]
        temp = sorted([int(x) for x in temp], reverse=True)
        if sum(temp) != 100000:
            raise AssertionError
        if len(temp) != 4:
            raise IndexError
        state["point"] = temp
    except AssertionError:
        await actuarial_point.finish("\n计分指令格式有误×\n请检查点数和是否为100000（采用起始点数25000的规则）。\n例：/计分 31000 24000 27000 18000", at_sender = True)
    except Exception:
        await actuarial_point.finish("\n计分指令格式有误×\n请检查点数个数并用空格分隔指令。\n例：/计分 31000 24000 27000 18000", at_sender = True)

@actuarial_point.handle()
async def jisuan(bot:Bot, event:Event, state:T_State = State()):
    shunweimadian = [+15,+5,-5,-15]
    state["ac_point"] = list() # 记录精算点的列表
    for i in range(4):
        state["ac_point"].append((state["point"][i]-25000)/1000 + shunweimadian[i])
    await actuarial_point.send(
'\n精算点计算成功~\n=========\n\
【一位马点】 {:+}\n\
【二位马点】 {:+}\n\
【三位马点】 {:+}\n\
【四位马点】 {:+}\n\
=========\n采用雀魂马点计算规则，\n\
精算原点25000，顺位马+15、+5、-5、-15。'.format(state["ac_point"][0], state["ac_point"][1], state["ac_point"][2], state["ac_point"][3]), at_sender = True)


# @actuarial_point.got("markdown","是否要记录本场牌局呢数据~\n回复“是”或者“1”进行记录。")
# async def _(bot:Bot, event:Event, state:T_State = State()):
#     if state["markdown"] != '1' or state["markdown"] != "是":
#         await actuarial_point.finish("已取消记录~")