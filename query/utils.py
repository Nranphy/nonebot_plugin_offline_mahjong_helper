from typing import Tuple
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from random import choice
from io import BytesIO



def majsoul_level_count(id:int,score:int,delta:int) -> Tuple[str,int,int]:
    """
    根据雀魂牌谱屋API传回的信息计算出段位及分数
    :rtype: 返回段位全称、现分数、段位上限分数元组
    """
    majsoul_level_map = {
        10301:{"level":"雀杰1","origin_score":600,"max_score":1200},
        10302:{"level":"雀杰2","origin_score":700,"max_score":1400},
        10303:{"level":"雀杰3","origin_score":1000,"max_score":2000},
        10401:{"level":"雀豪1","origin_score":1400,"max_score":2800},
        10402:{"level":"雀豪2","origin_score":1600,"max_score":3200},
        10403:{"level":"雀豪3","origin_score":1800,"max_score":3600},
        10501:{"level":"雀圣1","origin_score":2000,"max_score":4000},
        10502:{"level":"雀圣2","origin_score":3000,"max_score":6000},
        10503:{"level":"雀圣3","origin_score":4500,"max_score":9000},
        10701:{"level":"魂天1","origin_score":1000,"max_score":2000},
        10702:{"level":"魂天2","origin_score":1000,"max_score":2000},
        10703:{"level":"魂天3","origin_score":1000,"max_score":2000},
        10704:{"level":"魂天4","origin_score":1000,"max_score":2000},
        10705:{"level":"魂天5","origin_score":1000,"max_score":2000},
        10706:{"level":"魂天6","origin_score":1000,"max_score":2000},
        10707:{"level":"魂天7","origin_score":1000,"max_score":2000}}
    
    # 掉段特殊情况(只考虑掉雀士)
    if id==10301 and score+delta<0:
        return ("雀士3",500,1000)
    
    level_info = majsoul_level_map[id]
    true_socre = score+delta
    return (level_info["level"], true_socre, level_info["max_score"])

def img_util() -> Image.Image:
    img_path = Path(__file__).parent / Path("img/")
    background = Image.open(choice(list(img_path.iterdir())),'r')  # 请使用768*1024的图片

    draw = ImageDraw.Draw(background)
    draw.rectangle((100,200,100,200),"white")

    return background


if __name__=='__main__':
    img_util().show()