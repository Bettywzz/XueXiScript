#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: xlser.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-08-04(星期天) 07:13
@Copyright © 2019. All rights reserved.
'''
import re
import xlwings as xw
from .. import logger
from ..model import Bank

class Xlser(object):
    def __init__(self, path):
        self.path = path
        

    
    def load(self):  
        data = []      
        app=xw.App(visible=False,add_book=False)
        wb = app.books.open(self.path)
        ws = wb.sheets['bank']
        rng = ws.used_range
        logger.debug(rng.rows[0].value)
        for row in rng.rows[1:]:
            res = (row.value[1]).replace(u'\xa0', ' ')
            bank = Bank.from_challenge(content=res, answer=row.value[6])
            data.append(bank)
        wb.close()
        app.quit()
        return data

    def save(self, data):
        app=xw.App(visible=False,add_book=False)
        wb=app.books.add()
        ws = wb.sheets['Sheet1']
        # 写入数据
        print(f'{len(data)}条数据正在导出...')
        ws.range(1, 1).value = ['序号', '答案', '题干', '选项A', '选项B', '选项C', '选项D', '说明']
        try:
            for i, item in enumerate(data):
                ws.range(i+2, 1).value = item.to_array()
        except Exception:
            logger.debug(f'xls写入失败')
        finally:
            wb.save(self.path)
            wb.close()
            app.quit()
        return 0
