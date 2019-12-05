#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: quizXue
@file: viewer.py
@author: kessil
@contact: https://github.com/kessil/quizXue/
@time: 2019-08-08(星期四) 22:47
@Copyright © 2019. All rights reserved.
'''

from time import sleep
from .. import logger, cfg
from ..common import timer

class Viewer:
    '''设计思路：
        1. 点击‘百灵’，下拉刷新
        2. 点击第一个视频进入观看
        3. 延时指定时间后上划屏幕，进入下一则视频
        4. 重复步骤3直到完成指定视频数
        5. 右划退出观看，点击Home返回首页
    '''
    def __init__(self, rules, ad, xm):
        self.rules = rules
        self.ad = ad
        self.xm = xm
        self.home = 0j
        self.ding = 0j

    def _fresh(self):
        sleep(1)
        self.ad.uiautomator()
        self.xm.load()

    def enter(self):
        '''进入，点击百灵、刷新、点击第一条视频'''
        logger.info(f'视听学习中...')
        self._fresh()
        self.home = self.xm.pos(cfg.get(self.rules, 'rule_bottom_work'))
        logger.debug(f'HOME: {self.home}')
        self.ding = self.xm.pos(cfg.get(self.rules, 'rule_bottom_ding'))
        logger.debug(f'DING: {self.ding}')
        try:
            self.ad.tap(self.ding)
        except Exception as e:
            raise AttributeError(f'没有找到 百灵 的点击坐标')
        self._fresh()
        video_column = cfg.get('common', 'video_column_name')
        pos_col = self.xm.pos(f'//node[@text="{video_column}"]/@bounds')
        try:
            self.ad.tap(pos_col) # 点击{video_column}刷新
            logger.debug(f'百灵 {video_column}：{pos_col}')
        except Exception as e:
            logger.debug(f'百灵 {video_column} 不知道为什么找不到了 摊手')
            logger.debug(e)
        finally:
            self.ad.tap(self.ding) # 再点一次百灵刷新
        sleep(3)
        self._fresh()
        first = self.xm.pos(cfg.get(self.rules, 'rule_first_video'))
        logger.debug(f'第一个视频： {first}')
        self.ad.tap(first)

    def next(self):
        '''下一条，上划'''
        logger.debug(f'下一条')
        self.ad.draw('up', 200)
       

    def exit(self):
        '''点击HOME'''
        # self.ad.draw('right')
        self.ad.back()
        logger.debug(f'返回按钮事件')
        sleep(2)
        # self._fresh()        
        self.ad.tap(self.home)
        logger.debug(f'点击HOME {self.home}')
        sleep(5)

    def run(self, count=35, delay=45):
        '''运行脚本，count刷视频数，delay每个视频观看时间'''
        self.enter()
        while count:
            with timer.Timer() as t:          
                count -= 1
                sleep(5)
                # logger.info(f'正在视听学习 第 {count+1:2} 条，还剩 {count:2} 条，{delay:2} 秒后进入下一条...')
                logger.debug(f'观看{delay}秒中...')            
                sleep(delay)
                self.next()
            logger.info(f'视听学习第 {count} 则，耗时 {round(t.elapsed, 2):<05} 秒')
        # sleep(1200)
        self.exit()
        logger.info(f'视听学习完成，返回首页')

if __name__ == "__main__":
    from pathlib import Path
    from argparse import ArgumentParser
    from ..common import adble, xmler
    logger.debug('running viewer.py')
    parse = ArgumentParser()
    parse.add_argument('-c', '--count', metavar='count', type=int, default=36, help='观看视频数')
    parse.add_argument('-d', '--delay', metavar='delay', type=int, default=30, help='单个视频观看时间')
    parse.add_argument('-v', '--virtual', metavar='virtual', nargs='?', const=True, type=bool, default=False, help='是否模拟器')

    args = parse.parse_args()
    path = Path('./xuexi/src/xml/viewer.xml')
    ad = adble.Adble(path, args.virtual)
    xm = xmler.Xmler(path)
    cg = Viewer('mumu', ad, xm)
    cg.run(args.count, args.delay)

    ad.close()