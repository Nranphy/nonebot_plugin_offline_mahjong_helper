"""查询雀魂和天凤战绩"""



from nonebot import on_command, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.params import State, CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message
from nonebot.log import logger

import httpx
import json
import time

from .utils import *




majsoul_query = on_command("雀魂查询",aliases={"查询雀魂","雀魂战绩"},priority=10,block=True)

# 天凤查询网站都有墙，而且多数群玩天凤的应该都不算多
# tenhou_query = on_command("天凤查询",aliases={"查询天凤","天凤战绩"},priority=10,block=True)






@majsoul_query.handle()
async def majsoul_query_ensure_index(bot: Bot, event: Event, state:T_State=State(), arg:Message=CommandArg()):
    name = arg.extract_plain_text().strip()
    user_info = json.loads(httpx.get(f"https://ak-data-1.sapk.ch/api/v2/pl4/search_player/{name}?limit=5").content)
    state["user_info"] = user_info
    if not len(user_info):
        await majsoul_query.finish(f"未找到名称包含【{name}】的玩家...\n雀魂查询数据来自雀魂牌谱屋，仅可查询段位金之间、玉之间及王座之间的牌谱。\nps.暂不支持三麻查询",at_sender=True)
    elif len(user_info)==1:
        state["index"] = 0
    else:
        user_info_message = []
        for i in range(len(user_info)):
            temp_level_info = majsoul_level_count(user_info[i]['level']['id'], user_info[i]['level']['score'], user_info[i]['level']['delta'])
            temp_str = f"【{i+1}】 {user_info[i]['nickname']} \n（{temp_level_info[0]} [{temp_level_info[1]}/{temp_level_info[2]}]）\n最后对局时间：{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(user_info[i]['latest_timestamp']))}"
            user_info_message.append(temp_str)
        
        await majsoul_query.send(f"查找到多个相关用户~\n直接回复对应序号进行该角色查询√\n=========\n"+'\n======\n'.join(user_info_message)+"\n=========",at_sender=True)


@majsoul_query.got("index")
async def majsoul_query_precess(bot: Bot, event: Event, state:T_State=State()):
    try:
        if isinstance(state["index"],Message):
            state["index"] = int(state["index"].extract_plain_text().strip())-1
            if state["index"]<0 or state["index"]>len(state["user_info"]):
                raise ValueError
    except:
        await majsoul_query.finish("你输入的编号不正确哦~请稍后重试吧...",at_sender=True)
    
    index = state["index"]
    user_info = state["user_info"]

    id = user_info[index]["id"]
    
    # 进行查询
    url_basic = f"https://ak-data-6.pikapika.me/api/v2/pl4/player_stats/{id}/1262304000000/{int(time.time() * 1000)}?mode=16.12.9.15.11.8"
    url_pro = f"https://ak-data-6.pikapika.me/api/v2/pl4/player_extended_stats/{id}/1262304000000/{int(time.time() * 1000)}?mode=16.12.9.15.11.8"
    user_data_basic = json.loads(httpx.get(url_basic).content)
    user_data_pro = json.loads(httpx.get(url_pro).content)
    # 基础数据处理
    nickname = user_data_basic["nickname"]  # 游戏昵称
    level_info = majsoul_level_count(user_data_basic["level"]["id"], user_data_basic["level"]["score"], user_data_basic["level"]["delta"]) # 段位信息
    max_level_info = majsoul_level_count(user_data_basic["max_level"]["id"], user_data_basic["max_level"]["score"], user_data_basic["max_level"]["delta"]) # 最高段位信息
    rank_retes = user_data_basic["rank_rates"] # 顺位率列表
    avg_rank = user_data_basic["avg_rank"] # 平均顺位
    negative_rate = user_data_basic["negative_rate"] # 被飞率
    # 进阶数据处理
        # 可直接在user_data_pro中获取和牌率,自摸率,默听率,放铳率,副露率,立直率,平均打点,最大连庄,和了巡数,平均铳点,流局率,流听率,一发率,里宝率,被炸率,平均被炸点数,放铳时立直率,放铳时副露率,立直后放铳率,立直后非瞬间放铳率,副露后放铳率,立直后和牌率,副露后和牌率,立直后流局率,副露后流局率,放铳至立直,放铳至副露,放铳至默听,立直和了,副露和了,默听和了,立直巡目,立直收支,立直收入,立直支出,先制率,追立率,被追率,振听立直率,立直好型,立直多面,立直好型2,役满,最大累计番数,W立直,打点效率,铳点损失,净打点效率,平均起手向听,平均起手向听亲,平均起手向听子
    
    await majsoul_query.finish(f"""
【昵称】 {nickname}
【记录段位】 {level_info[0]} [{level_info[1]}/{level_info[2]}]
【最高段位】 {max_level_info[0]} [{max_level_info[1]}/{max_level_info[2]}]
======
【顺位率】
1位：{rank_retes[0]:.2%}
2位：{rank_retes[1]:.2%}
3位：{rank_retes[2]:.2%}
4位：{rank_retes[3]:.2%}
平均顺位：{avg_rank:.2f}""",at_sender=True)




