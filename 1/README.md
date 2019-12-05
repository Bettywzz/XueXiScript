# 学习强国 AutoXue 2.3

## 有个事情必须在这里先声明，使用前请一定要看清楚README！这里提过的一些版本号、配置方法都是有用的

> **挑战答题 题库** [在线版1](./xuexi/src/md/data-doc.md) | [在线版2](./xuexi/src/md/data-grid.md) | [下载版](./xuexi/src/xls/data-dev.xlsx)

> 项目更名 AutoXue： 支持阅读文章、视听学习、每日答题、挑战答题，自由配置积分或积点点通，阅读文章支持收藏、分享、评论（支援评论列表整理请看[这里](./xuexi/src/json/comments.json)），每日可积分41分、积点点通33点



> 使用本项目直接下载zip 或者
```bash
$:git clone https://github.com/kessil/AutoXue.git --depth=1
```
## 环境要求
* os：Win10+
* Python：python 3.6+ 推荐[python 3.7.4](http://www.python.org/)
* ADB：ADB1.0.39+ 推荐[ADB 1.0.40](./xuexi/src/assets/ADB_1_0_40.7z)
* device：Android 推荐[MuMu模拟器](http://mumu.163.com/)

## 使用方法
0. 很重要！首先请确认自己的操作系统，XP系统只能安装python3.4-，请不要往下看了，项目要求python版本最低3.6，因为python3.6+加入了本项目使用的f-string特性，另、操作系统太低可能无法安装使用模拟器，所以，系统不符合的用户真心不要浪费时间往下看了
1. 安装好Python、ADB、MuMu模拟器，并**添加python和ADB环境变量**
2. 安装[ADBkeyboard](./xuexi/src/assets/ADBKeyboard.apk)输入法（解决输入中文,ADD版本过低将输入乱码，请注意ADB版本）
3. 安装[学习强国](https://www.xuexi.cn/)APP，测试版本为**2.5.0**
4. 双击运行初次安装.bat， 或者
```python
# 安装虚拟环境
python -m venv venv
# 安装项目依赖
(venv)$:python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
4. 打开MuMu模拟器（连接安卓手机需要开启USB调试），登录学习强国APP并置于首页
> 经测试，华为手机时有发生无法获取布局情况导致异常中断，其他手机未测试。强烈建议在模拟器中食用。作者不会考虑特别为某台设备做适配。

5. 确认配置(**强调！请不要使用Windows自带记事本修改配置，都会上GitHub的人我不用解释太多吧**)，[config-default.ini](./xuexi/config-default.ini)勿修改，在[config-custom.ini](./xuexi/config-custom.ini)中修改配置，积分或是积点点通做相应配置即可
> 修改方法： 从[config-default.ini](./xuexi/config-default.ini)复制需要改动的[section]和[option]到[config-custom.ini](./xuexi/config-custom.ini),注意，每条配置必须在其section下
>> 如：要修改模拟器连接端口，那么你的[config-custom.ini](./xuexi/config-custom.ini)应该像这样
```
; ./xuexi/config-custom.ini
[mumu]
port = 对应的端口号
```


| 配置值          | 积分 | 积点点通 | 备注           |
| ------------------ | :----: | :--------: | ---------------- |
| challenge_count    | 10+  | 30+      | 答对5题积3分上限6分 |
| video_count        | 6+   | 20+      | 要求6则，每则1分上限6分      |
| video_delay        | 180+ | 54+      | 总时长要求18分钟，每3分钟积1分上限6分 |
| article_count      | 6+   | 20+      | 要求6篇，每篇1分上限6分      |
| article_delay      | 120+ | 36+      | 总时长要求12分钟，每2分钟积1分上限6分 |
| star_share_comment | 2+   | 2+       | 不积点点通  |
6. 双击开始积分.bat， 或者
```python
# 运行脚本程序
(venv)$:python -m xuexi -a -c -d -v
''' 请在首页运行, 参数按需添加
参数说明
    -a[--article]:      阅读文章(已完成) 支持收藏、分享、留言
    -c[--challenge]:    挑战答题(已完成)
    -d[--daily]:        每日答题(已完成)
    -v[--video]:        视听学习(已完成)
'''
(venv)$:python -m xuexi.quiz.challenge -c 30 -v True|False
'''请进入挑战答题后运行，手机也支持，
参数说明
    -c[--count] 挑战答题题数<int>, 自己指定， 默认10
    -v[--virtual] 是否模拟器<bool>，配和config使用
    eg.
        (venv)$:python -m xuexi.quiz.challenge -c 30 -v # 模拟器中使用
        (venv)$:python -m xuexi.quiz.challenge -c 30 # 手机中使用
'''
(venv)$:python -m xuexi.media.viewer -c 20 -d 30 -v True|False
'''请在首页运行
参数说明
    -c[--count] 观看视频数<int>, 自己指定, 默认36
    -d[--delay] 每个视频观看时间<int>, 自己指定， 默认30
    -v[--virtual] 是否模拟器<bool>，配和config使用
    eg.
        (venv)$:python -m xuexi.media.viewer -c 20 -d 30 -v # 模拟器中使用
        (venv)$:python -m xuexi.media.viewer -c 20 -d 30 # 手机中使用 
'''
(venv)$:python -m xuexi.media.reader -c 20 -d 30 -v True|False
'''请在首页运行
参数说明
    -c[--count] 观看视频数<int>, 自己指定, 默认25
    -d[--delay] 每个视频观看时间<int>, 自己指定， 默认30
    -v[--virtual] 是否模拟器<bool>，配和config使用
    eg.
        (venv)$:python -m xuexi.media.reader -c 20 -d 30 -v # 模拟器中使用
        (venv)$:python -m xuexi.media.reader -c 20 -d 30 # 手机中使用 
'''
```
