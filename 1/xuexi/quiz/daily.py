#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: daily.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-07-30(星期二) 22:56
@Copyright © 2019. All rights reserved.
'''
import re
import json
from time import sleep
from pathlib import Path
from ..model import Bank, Model
from .. import logger, cfg



class DailyQuiz(object):
    def __init__(self, rules, ad, xm):
        logger.info('开始每日答题')
        self.rules = rules
        self.ad = ad
        self.xm = xm
        self.db = Model(cfg.get('common', 'database_daily'))
        self.filename = Path(cfg.get('common', 'daily_json'))
        self.catagory = ''
        self.content = ''
        self.options = ''
        self.answer = ''
        self.note = ''
        self.has_bank = False
        self.count_blank = 0
        self.json_blank = self._load()
        self.is_user = cfg.getboolean('common', 'is_user')
        self.p_submit = 0j
        self.p_back = 0j
        self.p_return = 0j
        self.p_next = 0j
        
    def _enter(self):
        self._fresh()
        pos = self.xm.pos(cfg.get(self.rules, 'rule_daily_entry'))
        self.ad.tap(pos)
        sleep(10)
 
    def _fresh(self):
        self.ad.uiautomator()
        self.xm.load()

    def _blank(self):
        self.content = self.xm.content(cfg.get(self.rules, 'rule_blank_content'))
        print(f'\n[{self.catagory}] {self.content[:45]}...')
        logger.debug(self.content)
        edits = self.xm.pos(cfg.get(self.rules, 'rule_edits'))
        
        logger.debug(edits)
        if isinstance(edits, list):
            self.count_blank = len(edits)
        else:
            self.count_blank = 1
            edits = [edits]
        bank = self.db.query(content=self.content, catagory='填空题')
        if bank:
            self.has_bank = True
            logger.info(f'自动提交答案: {bank.answer}')
            answers = bank.answer.split(' ')
            for edit, answer in zip(edits, answers):
                self.ad.tap(edit)
                self.ad.input(answer)
        else:
            logger.info(f'默认提交答案: 不忘初心牢记使命')
            self.options = f'{self.count_blank}'
            for edit in edits:
                self.ad.tap(edit)
                self.ad.input('不忘初心牢记使命')




    def _radio(self):
        self.content = self.xm.content(cfg.get(self.rules, 'rule_content'))
        print(f'\n[{self.catagory}] {self.content[:45]}...')
        logger.debug(self.content)
        options = self.xm.pos(cfg.get(self.rules, 'rule_options'))
        logger.debug(options)
        bank = self.db.query(content=self.content, catagory='单选题')
        if bank:   
            self.has_bank = True
            logger.info(f'自动提交答案: {bank.answer}')      
            self.ad.tap(options[ord(bank.answer)-65])
        else:
            logger.info(f'默认提交答案: A')
            self.answer = 'A'
            self.note = ''
            self.options = ''
            self.ad.tap(options[0])

    def _check(self):
        self.content = self.xm.content(cfg.get(self.rules, 'rule_content'))
        print(f'\n[{self.catagory}] {self.content[:45]}...')
        logger.debug(self.content)
        options = self.xm.pos(cfg.get(self.rules, 'rule_options'))
        logger.debug(options)
        
        bank = self.db.query(content=self.content, catagory='多选题')
        if bank:    
            self.has_bank = True      
            logger.info(f'自动提交答案: {bank.answer}') 
            for c in bank.answer:
                self.ad.tap(options[ord(c)-65])
        else:            
            self.answer = ''
            self.note = ''
            self.options = ''
            # 作者也不想如此丧心病狂，实在是因为平台居然出现过答案是ABCDEFGHI的题目
            answers = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split(' ')
            for option, answer in zip(options, answers):
                if 0j != option:
                    self.answer = self.answer + answer
                    self.ad.tap(option)
                # else:
                #     pass
            logger.info(f'默认提交答案: 全选')
            

    def _submit(self):
        logger.debug(f'提交')
        if self.p_submit == 0j:
            self._fresh()
            self.p_submit = self.xm.pos(cfg.get(self.rules, 'rule_submit'))
        self.ad.tap(self.p_submit)
    
    def _back(self):
        logger.debug(f'后退一步')
        if self.p_back == 0j:
            self._fresh()
            self.p_back = self.xm.pos(cfg.get(self.rules, 'rule_back'))
        self.ad.tap(self.p_back)

    def _next(self):
        logger.debug(f'再来一组')
        if self.p_next == 0j:
            self._fresh()
            self.p_next = self.xm.pos(cfg.get(self.rules, 'rule_next'))
        self.ad.tap(self.p_next)

    def _return(self):
        logger.debug(f'返回')
        if self.p_return == 0j:
            self._fresh()
            self.p_return = self.xm.pos(cfg.get(self.rules, 'rule_return'))
        self.ad.tap(self.p_return)

    def _desc(self):
        self._fresh()
        res = self.xm.content(cfg.get(self.rules, 'rule_desc'))
        logger.debug(res)
        if '' == res:
            return True
        else:
            self.answer = re.sub(r'正确答案：', '', res)
            return False

    def _note(self):
        res = self.xm.content(cfg.get(self.rules, 'rule_note'))
        logger.debug(res)
        return res

    def _save(self):
        if not self.has_bank and '未知题目类型' != self.catagory and '' != self.content:
            bank = Bank.from_daily(catagory=self.catagory, 
                                    content=self.content, 
                                    options=self.options, 
                                    answer=self.answer, 
                                    note=self.note)
            # logger.debug(str(bank))
            if self.catagory in "填空题单选题多选题":
                logger.info(f'正确答案: {self.answer}')
                if '填空题' == self.catagory and 1 < self.count_blank:
                    # fname = cfg.get('common', 'export_filename')
                    bank.options = f'{self.count_blank}'
                    self.json_blank.append(bank.to_dict()) 
                    logger.info(f'多项填空题写入json文件中')
                else:
                    self.db.add(bank)
                    # 用户刷的新题在json备一份
                    if self.is_user:
                        self.json_blank.append(bank.to_dict()) 

                

            

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



    def _type(self):
        self._fresh()
        return self.xm.content(cfg.get(self.rules, 'rule_type'))

    def _score_reached(self):
        sleep(3)
        self._fresh()
        res = self.xm.content(cfg.get(self.rules, 'rule_score_reached'))
        logger.debug(res)
        return '领取奖励已达今日上限' == res

    def _dispatch(self):
        self.has_bank = False
        self.catagory = self._type()
        if '填空题' == self.catagory:
            self._blank()
        elif '单选题' == self.catagory:
            self._radio()
        elif '多选题' == self.catagory:
            self._check()
        else:
            logger.info('未知题目类型')

        # print(f'\n[{self.catagory}] {self.content}')
        # 填好空格或选中选项后
        self._submit() # 点击确定
        # 提交答案后，获取答案解析，若为空，则回答正确，否则，返回正确答案
        if self._desc():
            logger.debug('回答正确')
            self.note = ''
            self._save()
        else:
            self.note = self._note()
            self._save()
            self._submit()  # 点击下一题或者完成
    

    def run(self):
        count = 5
        self._enter()
        # 每次回答5题，每日答题6组
        group = 0
        while True:
            print(f'\n<----正在答题,第 {group} 组---->')
            for j in range(count):
                self._dispatch()
            self._dump()
            if self._score_reached() and not cfg.getboolean('common', 'daily_forver'):
                logger.debug(f'分数已达标')
                break
            else:
                logger.debug(f'分数未达标, 再来一组')
                sleep(cfg.getint('common', 'daily_delay'))
                self._next()
                group += 1
        logger.debug(f'大战{group}回合，终于分数达标咯，告辞！')
        self.ad.back()
        return True

    def weekly(self, count=5):
        while count:
            count -= 1
            self._dispatch()



            

if __name__ == "__main__":
    from argparse import ArgumentParser
    from ..common import adble, xmler
    logger.debug('running daily.py')
    parse = ArgumentParser()
    # parse.add_argument('-c', '--count', metavar='count', type=int, default=1, help='每日答题组数')
    parse.add_argument('-v', '--virtual', metavar='virtual', nargs='?', const=True, type=bool, default=False, help='是否模拟器')

    args = parse.parse_args()
    path = Path('./xuexi/src/xml/daily.xml')
    ad = adble.Adble(path, args.virtual)
    xm = xmler.Xmler(path)
    cg = DailyQuiz('mumu', ad, xm)
    cg.run()

    # 每周答题，请先注释上一行,取消注释下一行，页面置于每周答题第一题，运行python -m xuexi.quiz.daily -v
    # cg.weekly() 

    ad.close()


