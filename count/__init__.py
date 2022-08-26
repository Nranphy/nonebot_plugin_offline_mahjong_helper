from nonebot import on_command
from nonebot.typing import T_State
from nonebot.params import State, CommandArg
from nonebot.adapters.onebot.v11 import Bot, Event





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



#因为感觉有些符番得到的点数和计算规律不同，所以采用查表的方法了。
oya_point_form = {
(20, 1): ("-","-"),
(20, 2): ("-","700ALL"),
(20, 3): ("-","1300ALL"),
(20, 4): ("-","2600ALL"),

(25, 1): ("-","-"),
(25, 2): ("2400","-"),
(25, 3): ("4800","1600ALL"),
(25, 4): ("9600","3200ALL"),

(30, 1): ("1500","500ALL"),
(30, 2): ("2900","1000ALL"),
(30, 3): ("5800","2000ALL"),
(30, 4): ("11600","3900ALL"),

(40, 1): ("2000","700ALL"),
(40, 2): ("3900","1300ALL"),
(40, 3): ("7700","2600ALL"),

(50, 1): ("2400","800ALL"),
(50, 2): ("4800","1600ALL"),
(50, 3): ("9600","3200ALL"),

(60, 1): ("2900","1000ALL"),
(60, 2): ("5800","2000ALL"),
(60, 3): ("11600","3900ALL"),

(70, 1): ("3400","1200ALL"),
(70, 2): ("6800","2300ALL"),

(80, 1): ("3900","1300ALL"),
(80, 2): ("7700","2600ALL"),

(90, 1): ("4400","1500ALL"),
(90, 2): ("8700","2900ALL"),

(100, 1): ("4800","1600ALL"),
(100, 2): ("9600","3200ALL"),

(110, 1): ("5300","-"),
(110, 2): ("10600","3600ALL")
        }

co_point_form = {
(20, 1): ("-","-"),
(20, 2): ("-","400,700"),
(20, 3): ("-","700,1300"),
(20, 4): ("-","1300,2600"),

(25, 1): ("-","-"),
(25, 2): ("1600","-"),
(25, 3): ("3200","800,1600"),
(25, 4): ("6400","1600,3200"),

(30, 1): ("1000","300,500"),
(30, 2): ("2000","500,1000"),
(30, 3): ("3900","1000,2000"),
(30, 4): ("7700","2000,3900"),

(40, 1): ("1300","400,700"),
(40, 2): ("2600","700,1300"),
(40, 3): ("5200","1300,2600"),

(50, 1): ("1600","400,800"),
(50, 2): ("3200","800,1600"),
(50, 3): ("6400","1600,3200"),

(60, 1): ("2000","500,1000"),
(60, 2): ("3900","1000,2000"),
(60, 3): ("7700","2000,3900"),

(70, 1): ("2300","600,1200"),
(70, 2): ("4500","1200,2300"),

(80, 1): ("2600","700,1300"),
(80, 2): ("5200","1300,2600"),

(90, 1): ("2900","800,1500"),
(90, 2): ("5800","1500,2900"),

(100, 1): ("3200","800,1600"),
(100, 2): ("6400","1600,3200"),

(110, 1): ("3600","-"),
(110, 2): ("7100","1800,3600")
        }

def point_counter(fu:int=20, han:int=1) -> list:
    '''
    对输入的符和番数返回对应点数计算值。
    :param fu: 和牌的符数
    :param han: 和牌的番数
    :返回查表成功与否布尔值、庄家和牌点数（荣和和自摸）元组、子家和牌点数（荣和和自摸）元组、备注。
    '''
    oya_point = oya_point_form.get((fu,han),None)
    co_point = co_point_form.get((fu,han),None)
    if oya_point:
        return [True,oya_point, co_point,"==="]
    elif han==5 or (han==4 and fu>=40) or (han==3 and fu>=70):
        return [True,("12000", "4000ALL"), ("8000", "2000,4000"),"满贯"]
    elif 6<=han<=7:
        return [True,("18000", "6000ALL"), ("12000", "3000,6000"),"跳满"]
    elif 8<=han<=10:
        return [True,("24000", "8000ALL"), ("16000", "4000,8000"),"倍满"]
    elif 11<=han<=12:
        return [True,("36000", "12000ALL"), ("24000", "6000,12000"),"三倍满"]
    elif han>=13:
        return [True,("48000", "16000ALL"), ("32000", "8000,16000"),"累计役满"]
    else:
        oya = 6 * fu * pow(2,han+2)
        co = 4 * fu * pow(2,han+2)
        return [False, oya, co]