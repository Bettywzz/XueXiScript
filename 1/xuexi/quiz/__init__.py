#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: __init__.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-04(星期天) 19:27
@Copyright © 2019. All rights reserved.
'''
import re
import json
from time import sleep
from ..common import adble, xmler
from .. import logger, cfg
from .challenge import ChallengeQuiz
from .daily import DailyQuiz

class Quiz(object):
    def __init__(self, rules, ad, xm):
        self.rules = rules
        self.ad = ad
        self.xm = xm

        self.home = 0j
        self.mine = 0j
        self.back = 0j

    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    def _run_daily(self):

        dq = DailyQuiz(self.rules, self.ad, self.xm)
        # score = cfg.getint('common', 'daily_score')
        # count = 5 # cfg.getint('common', 'daily_count')
        dq.run()
        logger.info('完成每日答题，请稍候片刻...')
        # sleep(5)

    def _run_challenge(self):

        cq = ChallengeQuiz(self.rules, self.ad, self.xm)
        count = cfg.getint('common', 'challenge_count')
        cq.run(count)
        logger.info('完成挑战答题，请稍候片刻...')
        # sleep(5)

    def start(self, day, chg):
        # 刷新一下
        self.ad.draw('down')
        sleep(3)

        # 点击我的
        self._fresh()
        self.home = self.xm.pos(cfg.get(self.rules, 'rule_bottom_work'))
        self.mine = self.xm.pos(cfg.get(self.rules, 'rule_bottom_mine'))
        self.ad.tap(self.mine)

        # 点击我要答题
        sleep(2)
        self._fresh()
        pos = self.xm.pos(cfg.get(self.rules, 'rule_quiz_entry'))
        self.ad.tap(pos)
        logger.debug(f'我要答题这里等10秒钟，布局刷新比较慢')
        sleep(10)
        self._fresh()
        self.back = self.xm.pos(cfg.get(self.rules, 'rule_quiz_exit'))
        if day:
            logger.debug(f'开始每日答题')
            self._run_daily()
            sleep(5)
        else:
            logger.debug(f'未选择执行每日答题')
        if chg:
            logger.debug(f'开始挑战答题')
            self._run_challenge()
            sleep(5)
        else:
            logger.debug(f'未选择执行挑战答题')

        # 退出我要答题
        # sleep(2)
        self.ad.tap(self.back)
        self.ad.tap(self.home)
        sleep(5)
