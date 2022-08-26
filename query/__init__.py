"""查询雀魂和天凤战绩"""



from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import State, CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event, Message, MessageSegment
from nonebot.log import logger

import httpx
import json
import time
from pathlib import Path

from nonebot_plugin_htmlrender import md_to_pic

from .utils import *




majsoul_query = on_command("雀魂查询",aliases={"查询雀魂","雀魂战绩"},priority=10,block=True)

# 暂时没写
# tenhou_query = on_command("天凤查询",aliases={"查询天凤","天凤战绩"},priority=10,block=True)






@majsoul_query.handle()
async def majsoul_query_ensure_index(bot: Bot, event: Event, state:T_State=State(), arg:Message=CommandArg()):
    name = arg.extract_plain_text().strip()
    user_search_pl4 = json.loads(httpx.get(f"https://4.data.amae-koromo.com/api/v2/pl4/search_player/{name}?limit=3").content)
    user_search_pl3 = json.loads(httpx.get(f"https://4.data.amae-koromo.com/api/v2/pl3/search_player/{name}?limit=3").content)
    user_id = []
    user_search = []
    for user in user_search_pl4+user_search_pl3:
        if user["id"] not in user_id:
            user_search.append(user)
            user_id.append(user["id"])
    state["user_info"] = user_search

    if not user_search:
        await majsoul_query.finish(f"未找到名称包含【{name}】的玩家...\n雀魂查询数据来自雀魂牌谱屋，仅可查询段位金之间、玉之间及王座之间的牌谱。",at_sender=True)
    elif len(user_search)==1:
        state["index"] = 0
    else:
        user_search_message = []
        for i in range(len(user_search)):
            temp_level_info = majsoul_level_count(user_search[i]['level']['id'], user_search[i]['level']['score'], user_search[i]['level']['delta'])
            temp_str = f"【{i+1}】 {user_search[i]['nickname']} \n（{temp_level_info[0]} [{temp_level_info[1]}/{temp_level_info[2]}]）\n最后对局时间：{time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(user_search[i]['latest_timestamp']))}"
            user_search_message.append(temp_str)
        
        await majsoul_query.send(f"查找到多个相关用户~\n直接回复对应序号进行该角色查询√\n=========\n"+'\n======\n'.join(user_search_message)+"\n=========",at_sender=True)


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
    ## 四麻
    url_basic_pl4 = f"https://4.data.amae-koromo.com/api/v2/pl4/player_stats/{id}/1262304000000/{int(time.time() * 1000)}?mode=16.12.9.15.11.8"
    url_pro_pl4 = f"https://4.data.amae-koromo.com/api/v2/pl4/player_extended_stats/{id}/1262304000000/{int(time.time() * 1000)}?mode=16.12.9.15.11.8"
    user_data_basic_pl4 = json.loads(httpx.get(url_basic_pl4).content)
    user_data_pro_pl4 = json.loads(httpx.get(url_pro_pl4).content)
    ## 三麻
    url_basic_pl3 = f"https://4.data.amae-koromo.com/api/v2/pl3/player_stats/{id}/1262304000000/{int(time.time() * 1000)}?mode=26.24.22.25.23.21"
    url_pro_pl3 = f"https://4.data.amae-koromo.com/api/v2/pl3/player_extended_stats/{id}/1262304000000/{int(time.time() * 1000)}?mode=26.24.22.25.23.21"
    user_data_basic_pl3 = json.loads(httpx.get(url_basic_pl3).content)
    user_data_pro_pl3 = json.loads(httpx.get(url_pro_pl3).content)

    # 基础数据处理
    ## 四麻
    if not user_data_basic_pl4.get("error",0):
        nickname = user_data_basic_pl4["nickname"]  # 游戏昵称
        level_info_pl4 = majsoul_level_count(user_data_basic_pl4["level"]["id"], user_data_basic_pl4["level"]["score"], user_data_basic_pl4["level"]["delta"]) # 段位信息
        max_level_info_pl4 = majsoul_level_count(user_data_basic_pl4["max_level"]["id"], user_data_basic_pl4["max_level"]["score"], user_data_basic_pl4["max_level"]["delta"]) # 最高段位信息

        level_str_pl4 = f"""
====四麻====
【记录段位】 {level_info_pl4[0]} [{level_info_pl4[1]}/{level_info_pl4[2]}]
【最高段位】 {max_level_info_pl4[0]} [{max_level_info_pl4[1]}/{max_level_info_pl4[2]}]"""
    else:
        level_str_pl4 = ""
    ## 三麻
    if not user_data_basic_pl3.get("error",0):
        nickname = user_data_basic_pl3["nickname"]  # 游戏昵称
        level_info_pl3 = majsoul_level_count(user_data_basic_pl3["level"]["id"], user_data_basic_pl3["level"]["score"], user_data_basic_pl3["level"]["delta"]) # 段位信息
        max_level_info_pl3 = majsoul_level_count(user_data_basic_pl3["max_level"]["id"], user_data_basic_pl3["max_level"]["score"], user_data_basic_pl3["max_level"]["delta"]) # 最高段位信息

        level_str_pl3 = f"""
====三麻====
【记录段位】 {level_info_pl3[0]} [{level_info_pl3[1]}/{level_info_pl3[2]}]
【最高段位】 {max_level_info_pl3[0]} [{max_level_info_pl3[1]}/{max_level_info_pl3[2]}]"""
    else:
        level_str_pl3 = ""

    # 进阶数据处理
    data_pic = await data2pic(nickname,user_data_pro_pl4,user_data_pro_pl3)

    
    await majsoul_query.finish(MessageSegment.text(f"""
【昵称】 {nickname}{level_str_pl4}{level_str_pl3}
===详细信息===
""")+MessageSegment.image(data_pic),at_sender=True)


async def data2pic(nickname:str,userdata_pl4:dict,userdata_pl3:dict) -> bytes:
    '''将两种进阶数据转化为Markdown，进而转为图片'''
    data_keys = userdata_pl4.keys() if len(userdata_pl4)>=len(userdata_pl3) else userdata_pl3.keys()
    mdstr = f"""<div class="nickname" style="font-size:20px" align="center"><b>{nickname}雀魂详细信息</b></div>
| 统计数据 | 四麻 | 三麻 |
| :----: | :---- | :---- |"""
    for key in data_keys:
        if key=='count':
            mdstr += f"\n| **记录对局数** | {userdata_pl4.get(key,'未找到')} | {userdata_pl3.get(key,'未找到')} |"
            continue
        elif key in ['最近大铳','id','played_modes']:
            continue
        mdstr += f"\n| {key} | {userdata_pl4.get(key,'未找到')} | {userdata_pl3.get(key,'未找到')} |"
    return await md_to_pic(mdstr,css_path=Path(__file__).parent / Path("template/style.css"),width=700)