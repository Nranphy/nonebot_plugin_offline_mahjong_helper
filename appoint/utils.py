from nonebot import get_bot, get_driver
from nonebot.adapters.onebot.v11 import MessageSegment, Message
from nonebot.log import logger
from typing import List, Tuple, Union
import json
import time
from pathlib import Path

data_path = Path(f"./data/mahjong_table/")
valid_path = data_path / 'valid/'
overdue_path = data_path / 'overdue/'
index_path = data_path / 'index'

try:
    for path in (data_path, valid_path, overdue_path):
        if not path.exists():
            path.mkdir()
    if not index_path.exists():
        with open(index_path,"w") as f:
            f.write("1")
except:
    logger.error("[约桌功能] 创建牌桌数据目录失败...")

# 预约牌桌是否分群，默认为1
offline_mahjong_group_divide = get_driver().config.offline_mahjong_group_divide if hasattr(get_driver().config, "offline_mahjong_group_divide") else 1
# 加入牌桌上限人数，0为无限制，默认为4
offline_mahjong_join_limit = get_driver().config.offline_mahjong_join_limit if hasattr(get_driver().config, "offline_mahjong_join_limit") else 4
# 最后一人退出牌桌是否自动解散牌桌，默认为1
offline_mahjong_last_one_quit = get_driver().config.offline_mahjong_last_one_quit if hasattr(get_driver().config, "offline_mahjong_last_one_quit") else 1


def appoint_create(creator, group, place:str, date:str, qqs:list = [], sta_time:str="未定时间", end_time:str="未定时间", notes:str="无备注") -> Tuple[bool,Union[str,dict]]:
    """
    保存所传入数据为牌桌
    :param creator: 牌桌创建者qq
    :param group: 牌桌群号
    :param place: 牌桌地点
    :param date: 牌局日期，格式yyyy-MM-dd，可不加前导零
    :param sta_time: 开始时间,格式hh:mm
    :param end_time: 结束时间,格式hh:mm
    :param notes: 备注
    :rtype: 成功则返回True与信息字典，失败返回False与错误信息."""
    
    # 地址合法性检查
    if not place:
        return (False, "请填写约桌地址...")
        
    # 日期合法性检查
    date_check_result = date_check(date)
    if not date_check_result[0]:
        return date_check_result

    qqs = [int(qq) for qq in qqs]

    name = get_table_index()

    table_info = {
        "code":name,
        "creator":int(creator),
        "group":int(group),
        "place":place,
        "date":date_format(date),
        "start":sta_time,
        "end":end_time,
        "qqs":qqs,
        "notes":notes
    }

    if (valid_path/name).exists():
        return (False,"已存在完全相同的牌局...")
    try:
        with open(valid_path/name,"w",encoding="UTF-8-sig") as f:
            json.dump(table_info,f)
    except:
        return (False,"写入预约牌桌时失败...")
    
    increase_table_index()
    return (True,table_info)


def select_table(creator:Union[str,int]=None, group:Union[str,int]=None, place:str=None, date:str=None, qqs:list = []) -> List[dict]:
    '''根据传入的信息检索满足条件的牌桌'''
    all_need = []
    for file in valid_path.iterdir():
        try:
            with open(file,"r",encoding="UTF-8-sig") as f:
                temp_data = json.load(f)
        except:
            logger.error(f"牌桌文件读取错误...错误文件名【{file}】.")
            continue
        if creator and ((creator.isdigit() and int(creator) != temp_data["creator"]) or (creator not in get_group_member_card(group,temp_data["creator"]))):
            continue
        if offline_mahjong_group_divide:
            if group and int(group) != temp_data["group"]:
                continue
        if place and place not in temp_data["place"]:
            continue
        if date and date != temp_data["date"]:
            continue
        # 还未做通过QQ查询牌桌的功能
        # qqs = [int(qq) for qq in qqs]
        # if not set(qqs).issubset(set(temp_data["qqs"])):
        #     continue
        all_need.append(temp_data)
    return all_need


def join_table(joiner,table:str) -> Tuple[bool,Union[str,dict]]:
    '''将目标QQ号加入指定桌'''
    search_result = search_table(table)
    if not search_result[0]:
        return search_result
    target_table = search_result[1]
    try:
        with open(target_table,"r",encoding="UTF-8-sig") as f:
            origin_data = json.load(f)
    except:
        return (False,"解析牌桌文件时出错...")
        
    try:
        if offline_mahjong_join_limit:
            if len(origin_data["qqs"])>=offline_mahjong_join_limit:
                return (False,f"牌桌人数已满{offline_mahjong_join_limit}人...")
        if int(joiner) in origin_data["qqs"]:
            return (False,"加入者已在牌桌中...")
        origin_data["qqs"].append(int(joiner))
    except:
        return (False,"牌桌文件内容有误...")
    with open(target_table,"w",encoding="UTF-8-sig") as f:
        f.truncate()
        json.dump(origin_data,f)
    return (True,origin_data)


def quit_table(bolter,table:str) -> Tuple[bool,Union[str,dict]]:
    '''将目标QQ号退出指定桌'''
    search_result = search_table(table)
    if not search_result[0]:
        return search_result

    target_table = search_result[1]
    try:
        with open(target_table,"r",encoding="UTF-8-sig") as f:
            origin_data = json.load(f)
    except:
        return (False,"解析牌桌文件时出错...")
    
    try:
        if int(bolter) not in origin_data["qqs"]:
            return (False,"退出者不在牌桌中...")
        origin_data["qqs"].remove(int(bolter))
    except:
        return (False,"牌桌文件内容有误...")
    if origin_data["qqs"] or offline_mahjong_last_one_quit:
        with open(target_table,"w",encoding="UTF-8-sig") as f:
            f.truncate()
            json.dump(origin_data,f)
        return (True,f"退出牌桌成功，牌桌目前有{len(origin_data['qqs'])}人")
    else:
        delete_table(target_table)  # 牌桌人数为0时自动删除牌桌
        return (True,"退出牌桌成功，牌桌所剩人数为0，牌桌已删除")

def delete_table(table:Path):
    '''将不需要的牌桌移入过期牌桌目录'''
    table.replace(overdue_path / table.name)

def search_table(code:str) -> Tuple[bool,Union[str,Path]]:
    '''根据传入的桌号寻找牌桌'''
    target_table = None

    if not code.isdigit():
        return (False,"桌号错误，应为五位纯数字...")
    
    for file in valid_path.iterdir():
        if file.name == code:
            target_table = file
    if not target_table:
        return (False,"未找到指定牌桌...")
    else:
        return (True,target_table)

def read_table(path:Path) -> dict:
    '''根据传入的正确Path读取牌桌文件并返回'''
    try:
        with open(path,"r",encoding="UTF-8-sig") as f:
            origin_data = json.load(f)
        return origin_data
    except:
        raise

def at_all_joiner(path:Path) -> Message:
    '''根据传入的正确Path返回对每个参与者at的Message'''
    try:
        info = read_table(path)
        return Message([MessageSegment.at(qq) for qq in info["qqs"]])
    except:
        raise

def get_joiner_number(path:Path) -> int:
    '''根据传入的正确Path返回牌桌参与者人数'''
    try:
        info = read_table(path)
        return len(info["qqs"])
    except:
        return 0


def get_now_date() -> str:
    '''返回标准化的当日日期'''
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())[:10]

def date_format(orginal:str) -> str:
    '''标准化日期写法，只接受1970-1-1与1970-01-01式的正确日期.程序以1970-01-01为标准.'''
    date_info = orginal.split('-')
    return f"{int(date_info[0]):04}-{int(date_info[1]):02}-{int(date_info[2]):02}"

def date_check(date:str) -> Tuple[bool,str]:
    '''日期格式检测'''
    date_now = get_now_date()
    if not date:
        return (False, "请填写约桌日期...")
    else:
        date_items = date.split('-')
        if len(date_items)!=3:
            return (False,"日期格式错误，请用1970-01-01或1970-1-1的格式哦...")
        if not date_items[0].isdigit() or len(date_items[0])!=4 or int(date_items[0])<=0:
            return (False,"日期年份填写错误...")
        elif date_items[0]<date_now[:4]:
            return (False,"牌桌年份已过期...")
        elif int(date_items[0])>int(date_now[:4])+1:
            return (False,"暂不支持更远时间的预约...")
        
        if not date_items[1].isdigit() or int(date_items[1])>12 or int(date_items[1])<=0:
            return (False,"日期月份填写错误...")
        elif int(date_items[0])==int(date_now[:4]) and int(date_items[1])<int(date_now[5:7]):
            return (False,"牌桌月份已过期...")
        
        days_map = [31,29,31,30,31,30,31,31,30,31,30,31] if int(date_items[0])%400==0 or (int(date_items[0])%4==0 and int(date_items[0])%100!=0) else [31,28,31,30,31,30,31,31,30,31,30,31]
        if not date_items[2].isdigit() or int(date_items[2])>days_map[int(date_items[1])-1] or int(date_items[2])<=0:
            return (False,"日期填写错误...")
        elif int(date_items[0])==int(date_now[:4]) and int(date_items[1])==int(date_now[5:7]) and int(date_items[2])<int(date_now[8:]):
            return (False,"日期已过期...")
    return (True,'')


async def get_group_member_card(group_id:Union[int,str], user_id:Union[int,str], no_cache:bool=False) -> str:
    '''获取群成员的称呼，调用协议端api'''
    bot = get_bot()
    group_id,user_id = int(group_id),int(user_id)
    try:
        info = await bot.call_api("get_group_member_info",group_id=group_id, user_id=user_id, no_cache=no_cache)
        return info["card"] if info["card"] else info["nickname"]
    except:return "隔壁牌友"

def get_table_index() -> str:
    '''获得当前牌桌排序序号'''
    try:
        with open(index_path,"r") as f:
            index = int(f.read())
    except:
        logger.error("[约桌功能] 牌桌序号文件内容出错...")
        index = 0
    return "{:05}".format(index)

def increase_table_index():
    '''牌桌排序序号+1'''
    try:
        with open(index_path,"r+") as f:
            index = int(f.read())
            f.seek(0)
            f.write(str(index+1))
    except:
        logger.error("[约桌功能] 牌桌序号文件内容出错，序号增加失败...")