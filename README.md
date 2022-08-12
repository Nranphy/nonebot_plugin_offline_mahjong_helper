# nonebot_plugin_offline_mahjong_helper
## 基于NoneBot2的面麻助手插件

* * *

### 简介

这个插件可以简单的实现面麻群中常常会有的约桌、查分、计分、算点等需求。

本插件是从我的bot中解耦出来的，可能有些地方不够简洁，还望海涵。~~（当然，如果能提pr最好不过了！！）~~

### 使用方法

本插件除文件本身外，还可在.env中增加配置项。

1） 通过`git clone`将本仓库下的插件部署在你的bot插件目录下。

2） 可在机器人根目录下的.env中加入以下内容，缺失的内容将使用插件的默认配置：
```json
#mahjong
## 约桌每日提醒时间
offline_mahjong_remind_time = [{"HOUR":8,"MINUTE":0},{"HOUR":10,"MINUTE":0},{"HOUR":12,"MINUTE":0}]
## 牌桌预约是否分群查询，默认为1
offline_mahjong_group_divide = 1
## 加入牌桌限制人数，默认为4，0为无限制
offline_mahjong_join_limit = 4
```

3） 启动机器人测试是否正常工作。

### 指令

本插件凭功能分为几个模块，分别拥有不同的指令和具体功能。

#### 查询

`/雀魂查询 XXXXX` 通过牌谱屋的数据查询雀魂玩家的基本信息，XXXXX为玩家名称，若名称有多个对应查找项，可根据指示再次指定。

#### 计算

`/精算 xxxxx xxxxx xxxxx xxxxx` 根据雀魂标准进行点数精算。规则为起始点25000，顺位马点+15、+5、-5、-15

`/算点 xxx xxx` 或 `/算分 xxx xxx` 计算和牌点数，xxx分别为符数和番数，不用考虑顺序（因为番一般都比符小），会输出亲家子家和自摸荣和四种情况。由于通过查表实现，故一些不可能达成的番型不会得到结果，且无法计算青天井的规则（最高就亲家累满了...）。

#### 约桌

以下xxxxx均为牌桌唯一的编号，如02333

~~（本来是用散列做的像commit版本号一样的编号，被吐槽输入英文和数字太麻烦了）~~

`/约桌` 可查看创建约桌表格，按提示进行约桌

`/所有牌桌` 查看所有约桌（有配置项可以控制是否分群）

`/我的牌桌` 可查看与自己有关的所有牌桌

`/牌桌细节 xxxxx` 可查看目标牌桌的所有细节

`/牌桌查询` 可查询指定条件牌桌，请直接输入查看具体指示

`/加入牌桌 xxxxx` 加入指定编号的牌桌（有配置项可以控制最高人数）

`/退出牌桌 xxxxx` 同上，注意最后一人退出牌桌会导致牌桌解散

`/解散牌桌 xxxxx` 可以解散自己创建的牌桌

同时，加入、退出、解散牌桌会at相关的人进行提醒；约桌当天也可以设置定时提醒来提醒鸽子们（？）

### 未来

- [ ] 增加可选配置项，如牌桌最后一人退出是否自动解散牌桌。

- [ ] 改进牌桌内容存储方式，每个人QQ号和对应群号放一起，而非将群号独立出来。（有时候会需要跨群的，但是只存同一群号查群名片很麻烦）~~（有人可能会问为什么不存数据库...多数群的同时约桌量应该用不上数据库吧×）~~

- [ ] 改进算符算点算法，而非通过查表方式，支持青天井等。（我没玩过这~~赌怪~~规则）

- [ ] 加入天凤查询。（主要是因为群里玩天凤雀龙门雀姬什么的太少了...）

- [ ] 加入雀魂查询详细内容，并生成图片返回防止刷屏。

- [ ] 加入其他新功能（雀魂抽卡模拟、分析牌谱、牌理分析等）

### 感谢

这次插件也用了好多大佬们的东西，感谢如下作者与仓库

[SAPikachu/amae-koromo](https://github.com/SAPikachu/amae-koromo) 雀魂牌谱屋，查询接口就用的这个，很详细，很厉害