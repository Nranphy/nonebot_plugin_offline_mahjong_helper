from nonebot import on_command, on_startswith, require, get_bot, get_driver
from nonebot.typing import T_State
from nonebot.params import State, CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment, Message
from nonebot.log import logger
from typing import Any, List, Union
import re
import time
import random
from pathlib import Path

from .utils import *
from .schedule import *

mahjong_appoint_help = on_command("约桌帮助",aliases={"牌桌帮助","约桌指南","牌桌指南"},priority=9,block=True)


mahjong_appoint_guide = on_command("约桌",aliases={"约战","线下约战","线下约桌","麻将约桌","麻将约战","预约牌桌","牌桌预约"},priority=10,block=True)

mahjong_appoint_create = on_startswith("【新建牌局】",priority=10,block=True)

mahjong_appoint_join = on_command("加入牌局",aliases={"加入牌桌","加入约桌"},priority=10,block=True)

mahjong_appoint_quit = on_command("退出牌局",aliases={"退出牌桌","退出约桌"},priority=10,block=True)

mahjong_appoint_list = on_command("约桌信息",aliases={"约战信息","牌桌信息","查看约桌","查看约战","查看牌桌","所有约桌","所有牌桌","所有牌局"},priority=10,block=True)

mahjong_appoint_detail = on_command("约桌细节",aliases={"牌桌细节","牌桌详细","约桌详细"},priority=10,block=True)

mahjong_appoint_list_mine = on_command("我的约桌",aliases={"我的约战","我的预约","我的牌桌","我的牌局"},priority=10,block=True)

mahjong_appoint_list_query = on_command("约桌查询",aliases={"约战查询","预约查询","查询约桌","查询约战","查询牌桌","查询预约","牌桌查询"},priority=10,block=True)

mahjong_appoint_dissolve = on_command("解散牌桌",aliases={"解散约桌","解散牌局"},priority=10,block=True)



@mahjong_appoint_help.handle()
async def mahjong_appoint_help_process():
    await mahjong_appoint_help.send('''约桌功能指南
【/约桌】可查看约桌表格，进行约桌
【/所有牌桌】查看所有群预约的牌桌
【/我的牌桌】可查看与自己有关的所有牌桌
【/牌桌细节 xxxxx】可查看牌桌的所有细节
【/牌桌查询】可查询指定条件牌桌，请直接输入查看具体指示
【/加入牌桌 xxxxx】加入指定编号的牌桌
【/退出牌桌 xxxxx】同上，注意最后一人退出牌桌会导致牌桌解散
【/解散牌桌 xxxxx】可以解散自己创建的牌桌''')


@mahjong_appoint_guide.handle()
async def mahjong_appoint_guide_process(bot:Bot, event:Event, state:T_State=State()):
    await mahjong_appoint_guide.send("请直接复制并改写以下表格新建约桌，请按照对应格式填写信息，带*项为必填信息。",at_sender=True)
    date_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())[:10]
    await mahjong_appoint_guide.send(
f'''【新建牌局】
=========
【*地点】渝中区千夜麻将
【*日期】{date_now}
【*开始时间】15:00
【*结束时间】18:00
【备注】无烟局，谢谢。'''
    )
    

@mahjong_appoint_create.handle()
async def mahjong_appoint_create_process(bot:Bot, event:Event, state:T_State=State()):
    message = event.get_plaintext()
    try:
        place = re.search("(?<=【\*地点】).*$",message,re.U|re.M).group().strip()
        date = re.search("(?<=【\*日期】).*$",message,re.U|re.M).group().strip()
        sta_time = re.search("(?<=【\*开始时间】).*$",message,re.U|re.M).group().strip()
        end_time = re.search("(?<=【\*结束时间】).*$",message,re.U|re.M).group().strip()
    except:
        await mahjong_appoint_create.finish("表格填写格式错误，创建牌桌失败...",at_sender=True)
    try:notes = re.search("(?<=【备注】).*$",message,re.U|re.M).group()
    except:notes = '无备注。'
    result = appoint_create(event.user_id,event.group_id,place,date,[event.user_id],sta_time,end_time,notes)
    if not result[0]:
        await mahjong_appoint_create.finish(f"创建牌桌失败，{result[1]}",at_sender=True)
    else:
        await mahjong_appoint_create.finish(f"创建牌桌成功~牌桌编号为 {result[1]['code']}\n可通过指令【/所有牌桌】或【/我的牌桌】查看牌桌列表。",at_sender=True)


@mahjong_appoint_join.handle()
async def mahjong_appoint_join_process(bot:Bot, event:Event, state:T_State=State(), arg:Message=CommandArg()):
    table = arg.extract_plain_text().strip()
    if not table:
        await mahjong_appoint_join.finish("请在指令后跟上具体的牌桌编号，以区分各牌桌。\n如：【/加入牌桌 12345】")
    try:at_message = at_all_joiner(search_table(table)[1])
    except:pass
    result = join_table(event.user_id,table)
    if not result[0]:
        await mahjong_appoint_join.finish(f"加入牌桌失败，{result[1]}",at_sender=True)
    else:
        await mahjong_appoint_join.send(f"加入牌桌成功~以下为牌桌基础信息：\n=========\n【地点】{result[1]['place']}\n【日期】{result[1]['date']}",at_sender=True)
        await mahjong_appoint_join.send(at_message+f"您加入的牌局有新成员加入了，当前加入人数为{get_joiner_number(search_table(table)[1])}.")

@mahjong_appoint_quit.handle()
async def mahjong_appoint_quit_process(bot:Bot, event:Event, state:T_State=State(), arg:Message=CommandArg()):
    table = arg.extract_plain_text().strip()
    if not table:
        await mahjong_appoint_quit.finish("请在指令后跟上具体的牌桌编号，以区分各牌桌。\n如：【/退出牌桌 12345】")
    try:at_message = at_all_joiner(search_table(table)[1])
    except:pass
    result = quit_table(event.user_id,table)
    if not result[0]:
        await mahjong_appoint_quit.finish(f"退出牌桌失败，{result[1]}",at_sender=True)
    else:
        await mahjong_appoint_quit.send(result[1],at_sender=True)
        await mahjong_appoint_quit.send(at_message+f"您加入的牌局有成员退出了...当前剩余人数为{get_joiner_number(search_table(table)[1])}.")
        


@mahjong_appoint_list.handle()
async def mahjong_appoint_list_process(bot:Bot, event:Event, state:T_State=State()):
    table_info = select_table(group=event.group_id) # 这里可以加参数更改默认查询参数
    state["table_info"] = table_info
    head_text = "现在所有约桌如下\n=========\n"
    body_text_part = []
    for index in range(len(table_info)):
        joiner = '，'.join([await get_group_member_card(event.group_id, qq) for qq in table_info[index]['qqs']])
        body_text_part.append(f"【{index+1}】({table_info[index]['code']}){table_info[index]['place']}（{'您创建的，' if table_info[index]['creator']==int(event.user_id) else ''}目前{len(table_info[index]['qqs'])}人{'，您已加入' if int(event.user_id) in table_info[index]['qqs'] else ''}）\n\
时间：{table_info[index]['date']}（{table_info[index]['start']}-{table_info[index]['end']}）\n\
参与者：{joiner}\n\
备注：{table_info[index]['notes']}")
    body_text = '\n======\n'.join(body_text_part)
    foot_text = "\n=========\n现可直接输入序号数字加入约桌，或可通过【/加入牌桌 12345】加入约桌，其中12345请改为牌桌序号后的编号。"
    await mahjong_appoint_list.send(head_text+body_text+foot_text,at_sender=True)

@mahjong_appoint_list.got("index")
async def mahjong_appoint_list_process_(bot:Bot, event:Event, state:T_State=State()):
    index = state["index"].extract_plain_text().strip()
    if not index.isdigit():
        await mahjong_appoint_list.finish()
    index = int(index)-1
    table_info = state["table_info"]
    if index>=len(table_info) or index<0:
        await mahjong_appoint_list.reject("输入数字过界，请重新输入数字...",at_sender=True)
    at_message = at_all_joiner(search_table(table_info[index]["code"])[1])
    result = join_table(event.user_id,table_info[index]["code"])
    if result[0]:
        await mahjong_appoint_list.send(f"加入牌桌成功~以下为牌桌基础信息：\n=========\n【地点】{result[1]['place']}\n【日期】{result[1]['date']}",at_sender=True)
        await mahjong_appoint_list.send(at_message+f"您加入的牌局有新成员加入了，当前加入人数为{get_joiner_number(search_table(table_info[index]['code'])[1])}.")
    else:
        await mahjong_appoint_list.reject(f"加入牌桌失败，{result[1]}\n可输入数字重试加入其他牌桌",at_sender=True)


@mahjong_appoint_detail.handle()
async def mahjong_appoint_detail_process(bot:Bot, event:Event, state:T_State=State(), arg:Message=CommandArg()):
    table = arg.extract_plain_text().strip()
    if not table:
        await mahjong_appoint_join.finish("请在指令后跟上具体的牌桌编号，以区分各牌桌。\n如：【/牌桌细节 12345】")
    search_result = search_table(table)
    if not search_result[0]:
        await mahjong_appoint_detail.finish(f"查询牌桌失败，{search_result[1]}",at_sender=True)
    try:
        with open(search_result[1],"r",encoding="UTF-8-sig") as f:
            table_info = json.load(f)
    except:
        await mahjong_appoint_detail.finish(f"查询牌桌失败，解析牌桌文件时出错...",at_sender=True)
    creator_member_card = await get_group_member_card(event.group_id, table_info["creator"])
    await mahjong_appoint_detail.finish(
        f'''已查询牌桌{table}的详细信息
=========
【创建者】{creator_member_card}({table_info["creator"]})
【地点】{table_info["place"]}
【日期】{table_info["date"]}
【开始时间】{table_info["start"]}
【结束时间】{table_info["end"]}
【备注】{table_info["notes"]}
【牌桌成员】'''+'，'.join([await get_group_member_card(event.group_id, qq) for qq in table_info["qqs"]]),at_sender=True)


@mahjong_appoint_list_mine.handle()
async def mahjong_appoint_list_process(bot:Bot, event:Event, state:T_State=State()):
    table_info = select_table() # 这里可以加参数更改默认查询参数
    state["table_info"] = table_info
    head_text = "关于你的约桌如下\n=========\n"
    body_text_part = []
    for index in range(len(table_info)):
        if (int(event.user_id) in table_info[index]['qqs']) or (int(event.user_id) == table_info[index]['creator']):
            joiner = '，'.join([await get_group_member_card(event.group_id, qq) for qq in table_info[index]['qqs']])
            body_text_part.append(f"【{index+1}】({table_info[index]['code']}){table_info[index]['place']}（{'您创建的，' if table_info[index]['creator']==int(event.user_id) else ''}目前{len(table_info[index]['qqs'])}人{'，您已加入' if int(event.user_id) in table_info[index]['qqs'] else ''}）\n\
时间：{table_info[index]['date']}（{table_info[index]['start']}-{table_info[index]['end']}）\n\
参与者：{joiner}\n\
备注：{table_info[index]['notes']}")
    body_text = '\n======\n'.join(body_text_part)
    foot_text = "\n=========\n若需要退出牌桌，可用指令【/退出牌桌 12345】退出约桌；若要解散自己创建的约桌，可用指令【/解散牌桌 12345】。其中12345请改为牌桌序号后的编号。"
    await mahjong_appoint_list_mine.send(head_text+body_text+foot_text,at_sender=True)


@mahjong_appoint_list_query.handle()
async def mahjong_appoint_list_query_process(bot:Bot, event:Event, state:T_State=State(), arg:Message=CommandArg()):
    parms = arg.extract_plain_text().strip().split()
    if not parms:
        await mahjong_appoint_list_query.finish("请在指令后加上具体的查询参数，目前支持日期、地址、QQ号的查询，格式为对应信息名与内容交替\n如：【/查询约桌 日期 1970-01-01 地点 渝中 QQ 123456】",at_sender=True)
    parms_zip = list(zip([parms[x] for x in range(0,len(parms),2)],[parms[x] for x in range(1,len(parms),2)]))
    for i in range(len(parms_zip)):
        parms_zip[i] = list(parms_zip[i])
        if parms_zip[i][0] in ["date","日期","时间"]:
            parms_zip[i][0] = "date"
            date_check_result = date_check(parms_zip[i][1])
            if not date_check_result[0]:
                await mahjong_appoint_list_query.finish(f"查询失败，{date_check_result[1]}",at_sender=True)
            else:
                parms_zip[i][1] = date_format(parms_zip[i][1])
        elif parms_zip[i][0] in ["place","地址","地点","地方","据点","位置","场所"]:
            parms_zip[i][0] = "place"
        elif parms_zip[i][0] in ["creator","桌主","创建者","主人","组织者"]:
            parms_zip[i][0] = "creator"
        # elif parms_zip[i][0] in ["qq","用户","人员"]:
        #     parms_zip[i][0] = "qqs"
        #     if not parms_zip[i][1].isdigit():
        #         await mahjong_appoint_list_query.finish("查询失败，QQ号格式有误...",at_sender=True)
        #     else:
        #         parms_zip[i][1] = [int(parms_zip[i][1])] # 没想好处理方法能让消息可以传入QQs数组
    parms_zip = dict(parms_zip)
    if not parms_zip.get("group"):
        parms_zip["group"]=event.group_id
    table_info = select_table(**parms_zip)
    state["table_info"] = table_info
    head_text = "满足条件的约桌如下\n=========\n"
    body_text_part = []
    for index in range(len(table_info)):
        joiner = '，'.join([await get_group_member_card(event.group_id, qq) for qq in table_info[index]['qqs']])
        body_text_part.append(f"【{index+1}】({table_info[index]['code']}){table_info[index]['place']}（{'您创建的，' if table_info[index]['creator']==int(event.user_id) else ''}目前{len(table_info[index]['qqs'])}人{'，您已加入' if int(event.user_id) in table_info[index]['qqs'] else ''}）\n\
时间：{table_info[index]['date']}（{table_info[index]['start']}-{table_info[index]['end']}）\n\
参与者：{joiner}\n\
备注：{table_info[index]['notes']}")
    body_text = '\n======\n'.join(body_text_part)
    foot_text = "\n=========\n现可直接输入序号数字加入约桌，或可通过【/加入牌桌 12345】加入约桌，其中12345请改为牌桌序号后的编号。"
    await mahjong_appoint_list_query.send(head_text+body_text+foot_text,at_sender=True)

@mahjong_appoint_list_query.got("index")
async def mahjong_appoint_list_process_(bot:Bot, event:Event, state:T_State=State()):
    index = state["index"].extract_plain_text().strip()
    if not index.isdigit():
        await mahjong_appoint_list_query.finish()
    index = int(index)-1
    table_info = state["table_info"]
    if index>=len(table_info) or index<0:
        await mahjong_appoint_list_query.reject("输入数字过界，请重新输入数字...",at_sender=True)
    at_message = at_all_joiner(search_table(table_info[index]["code"])[1])
    result = join_table(event.user_id,table_info[index]["code"])
    if result[0]:
        await mahjong_appoint_list_query.send(f"加入牌桌成功~以下为牌桌基础信息：\n=========\n【地点】{result[1]['place']}\n【日期】{result[1]['date']}",at_sender=True)
        await mahjong_appoint_list_query.send(at_message+f"您加入的牌局有新成员加入了，当前加入人数为{get_joiner_number(search_table(table_info[index]['code'])[1])}.")
    else:
        await mahjong_appoint_list_query.reject(f"加入牌桌失败，{result[1]}\n可输入数字重试加入其他牌桌",at_sender=True)


@mahjong_appoint_dissolve.handle()
async def mahjong_appoint_dissolve_process(bot:Bot, event:Event, state:T_State=State(), arg:Message=CommandArg()):
    table = arg.extract_plain_text().strip()
    if not table:
        await mahjong_appoint_join.finish("请在指令后跟上具体的牌桌编号，以区分各牌桌。\n如：【/加入牌桌 12345】")
    search_result = search_table(table)
    if not search_result[0]:
        await mahjong_appoint_dissolve.finish(f"解散牌桌失败，{search_result[1]}",at_sender=True)
    
    string = 'qwertyuiopasdfghjklzxcvbnm1234567890'
    state["random_str"] = ''.join([random.choice(string) for x in range(5)])
    state["path"] = search_result[1]
    table_info = read_table(search_result[1])
    if table_info["creator"] != int(event.user_id):
        await mahjong_appoint_dissolve.finish("非创建者无法创建牌桌，请联系创建者解散牌桌或使牌桌预约人数为0自动删除。\n若个人需要退出牌桌，请使用指令【/退出牌桌 12345】退出约桌，其中12345请改为牌桌编号。",at_sender=True)
    if len(table_info["qqs"])>1 or table_info["creator"] not in table_info["qqs"]:
        await mahjong_appoint_dissolve.send(f"已找到牌桌{table}，但预约参与者不止一人或仅有的参与者不为您。\n解散操作不可逆，若确认要解散并删除约桌，请再输入五位验证码【{state['random_str']}】以确认。",at_sender=True)
    else:
        state["sure"] = state["random_str"]

@mahjong_appoint_dissolve.got("sure")
async def mahjong_appoint_dissolve_process_(bot:Bot, event:Event, state:T_State=State()):
    if isinstance(state["sure"],Message):
        state["sure"] = state["sure"].extract_plain_text().strip()
    if state["sure"] != state["random_str"]:
        await mahjong_appoint_dissolve.finish("验证码错误，解散操作已取消...",at_sender=True)
    else:
        at_message = at_all_joiner(state["path"])
        delete_table(state["path"])
        await mahjong_appoint_dissolve.send("牌桌已解散并删除...",at_sender=True)
        await mahjong_appoint_dissolve.send(at_message+"您加入的约桌已被解散...请通过指令【/我的约桌】查看其他所有关于您的牌桌。")