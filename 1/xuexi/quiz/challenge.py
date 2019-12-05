#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: challenge.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-01(星期四) 20:55
@Copyright © 2019. All rights reserved.
'''
import re
import json
import requests
import string
from pathlib import Path
from random import randint
from urllib.parse import quote
from time import sleep
from ..model import Bank, Model
from .. import logger, cfg
from ..common.alarm import Alarm

class ChallengeQuiz(object):
    def __init__(self, rules, ad, xm):
        self.rules = rules
        self.filename = Path(cfg.get('common', 'challenge_json'))
        self.ad = ad
        self.xm = xm
        self.db = Model(cfg.get('common', 'database_challenge'))
        self.has_bank = False
        self.is_user = cfg.getboolean('common', 'is_user')
        # self.json_blank = self._load()
        self.content = ''
        self.options = ''
        self.note = ''
        self.answer = ''
        self.pos = ''
        self.p_back = 0j
        self.p_return = 0j
        self.p_share = 0j

    def _enter(self):
        self._fresh()
        pos = self.xm.pos(cfg.get(self.rules, 'rule_challenge_entry'))
        self.ad.tap(pos)
        logger.info(f'挑战答题，开始！')
        sleep(2)

    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    def _load(self):
        '''load json file'''
        filename = self.filename
        res = []
        if self.filename.exists():
            with open(filename,'r',encoding='utf-8') as fp:
                try:
                    res = json.load(fp)
                except Exception:
                    logger.debug(f'加载JSON数据失败')
                # logger.debug(res)
            logger.debug(f'载入JSON数据{filename}')
            return res
        else:
            logger.debug('JSON文件{filename}不存在')
            return res
        

    def _dump(self):
        '''save json file'''
        filename = self.filename
        with open(filename,'w',encoding='utf-8') as fp:
            json.dump(self.json_blank,fp,indent=4,ensure_ascii=False)
        logger.debug(f'导出JSON数据{filename}')
        return True

    def _search(self):
        logger.debug(f'search - {self.content}')
        Alarm('challenge.mp3', 1)
        '''搜索引擎检索题目'''
        content = re.sub(r'[\(（]出题单位.*', "", self.content)
        logger.info(f'\n[挑战题] {content}')
        url = quote('https://www.baidu.com/s?wd=' + content, safe=string.printable)
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
        response = requests.get(url, headers=headers).text
        counts = []
        for i, option in zip(['A', 'B', 'C', 'D'], self.options):
            count = response.count(option)
            counts.append((count, i))
            logger.info(f'{i}. {option}: {count}')
        counts = sorted(counts, key=lambda x:x[0], reverse=True)
        bank = None
        for item in self.json_blank:
            if item['content'] == self.content:
                bank = item
                break
            else:
                continue
        if bank:
            for c in counts:
                if c[1] in bank['note']:
                    continue
                else:
                    _, self.answer = c
                    break
        else:
            _, self.answer = counts[0]
        logger.info(f'试探性提交答案 {self.answer} 延时10秒中...')
        sleep(5)
        return ord(self.answer)-65
        



    def _content(self):
        res = self.xm.content(cfg.get(self.rules, 'rule_challenge_content'))
        logger.debug(res)
        return res
    
    def _optoins(self):
        res = self.xm.options(cfg.get(self.rules, 'rule_challenge_options_content'))
        logger.debug(res)
        return res

    def _pos(self):
        res = self.xm.pos(cfg.get(self.rules, 'rule_challenge_options_bounds'))
        logger.debug(res)
        return res

    def _submit(self):
        challenge_delay = cfg.getint('common', 'challenge_delay')        
        if 0 == challenge_delay:
            delay_seconds = randint(0, 5)
        else:
            delay_seconds = challenge_delay
        self._fresh()
        self.content = self._content()
        self.options = self._optoins()
        self.note = ''
        self.pos = self._pos()
        bank = self.db.query(content=self.content, catagory='挑战题')
        if bank is not None:
            options = "\n".join([f'{chr(i+65)}. {x}' for i, x in enumerate(self.options)])
            print(f'\n[挑战题] {self.content[:45]}...\n{options}')
            self.has_bank = True
            # logger.debug('bank from database')
            cursor = ord(bank.answer) - 65
            logger.info(f'自动提交答案 {bank.answer}')
            sleep(delay_seconds) # 延时按钮
        else:
            self.has_bank = False
            cursor = self._search()
            
        logger.debug(f'正确选项下标 {cursor}')
        # 点击正确选项
        while 0j == self.pos[cursor]:
            self.ad.draw('up')
            self._fresh()
            self.pos = self._pos()
        # 现在可以安全点击(触摸)
        self.ad.tap(self.pos[cursor])

    
    def _db_add(self):
        # from_challenge(cls, content, options, answer='',note='', bounds='')
        if not self.has_bank:
            bank = Bank.from_challenge(content=self.content, options=self.options, answer=self.answer, note='', bounds='')
            self.db.add(bank)
            if self.is_user:
                self.json_blank.append(bank.to_dict())
            

    def _reopened(self, repeat:bool=False)->bool:
        '''默认使用复活权,不使用再来一局'''
        # sleep(2)
        self._fresh()
        # 本题答对否
        if not self.xm.pos(cfg.get(self.rules, 'rule_judge_bounds')):
            self._db_add()
            return True
        else:
            # 在note中追加一个错误答案，以供下次遇到排除
            temp = None
            for item in self.json_blank:
                if item['content'] == self.content:
                    temp = item
            if temp:
                temp['note'] += self.answer
            else:
                temp = Bank.from_challenge(content=self.content, options=self.options, answer='', note=self.answer, bounds='')
                self.json_blank.append(temp.to_dict())
                logger.debug(f'错题加入错题集JSON文件中')
            logger.info(f'不要那么贪心，闪动的复活按钮不好点击，就此结束吧')
            return False
        
        # 分享复活否？ 否！ 由于复活按钮在闪动，不好点击，还是不要那么贪心吧
        # pos = self.xm.pos(cfg.get(self.rules, 'rule_revive_bounds'))
        # if pos:
        #     # self._commet()
        #     logger.debug('点击分享复活')
        #     logger.info('复活中，请稍等...')            
        #     self.ad.tap(pos, duration=200)
        #     sleep(10)
        #     self.ad.back()
        #     sleep(5)
        #     return True
        # return False
        
        # 再来一局否？
        # pos = self.xm.pos(cfg.get(self.rules, 'rule_again_bounds'))
        # if pos:
        #     self._commet()
        #     if repeat:
        #         logger.debug('点击再来一局')
        #         logger.info('开局中，请稍等...')
        #         sleep(10) # 平台奇葩要求，10秒内仅可答题一次
        #         self.ad.tap(pos)
        #         sleep(5)
        #         return True
        #     else:
        #         self.ad.back()
        #         return False
        # return True

    def _commet(self):
        maxlen = len(self.options)
        try:
            ch = input(f'请输入正确的答案: ').upper()
            assert ch in 'NABCD'[:maxlen+1],f"输入的项目不存在，请输入A-DN"
        except Exception as ex:
            print(f"输入错误:",ex)
        if ch in 'ABCD':
            self.answer = ch
            self._db_add()
        return ch
            

    def _run(self, count):
        # is_dead = False
        sub_count = count
        self._enter()
        while sub_count:
            self._submit()
            if self._reopened(): # 回答正确
                sub_count = sub_count - 1
            else:
                # is_dead = True
                break
        else:
            logger.info(f'已达成目标题数，延时30秒等待死亡中...')
            sleep(30)
        self.ad.back()   
        return sub_count

    def run(self, count):
        while True:
            self.json_blank = self._load()
            if 0 == self._run(count):
                logger.info(f'已达成目标题数 {count} 题，退出挑战')
                break
            else:
                sleep(3)
                logger.info(f'未达成目标题数，再来一局')
            self._dump()

    def runonce(self, sub_count):
        while sub_count:
            self._submit()
            if self._reopened(): # 回答正确
                sub_count = sub_count - 1
            else:
                break

if __name__ == "__main__":
    from argparse import ArgumentParser
    from ..common import adble, xmler
    logger.debug('running challenge.py')
    parse = ArgumentParser()
    parse.add_argument('-c', '--count', metavar='count', type=int, default=10, help='挑战答题题数')
    parse.add_argument('-v', '--virtual', metavar='virtual', nargs='?', const=True, type=bool, default=False, help='是否模拟器')

    args = parse.parse_args()
    path = Path('./xuexi/src/xml/challenge.xml')
    ad = adble.Adble(path, args.virtual)
    xm = xmler.Xmler(path)
    cg = ChallengeQuiz('mumu', ad, xm)
    cg.runonce(args.count)

    ad.close()



