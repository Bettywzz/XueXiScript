#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: xmler.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-07-31(星期三) 15:15
@Copyright © 2019. All rights reserved.
'''

import re
from pathlib import Path
from lxml import etree
from .. import logger

def str2complex(s):
    x0, y0, x1, y1 = [int(x) for x in re.findall(r'\d+', s)]
    logger.debug(f'({x0}, {y0}) -> ({x1}, {y1})')
    res = complex((x0+x1)//2, (y0+y1)//2)
    logger.debug(res)
    return res


class Xmler(object):
    def __init__(self, path=Path('./xuexi/src/xml/reader.xml')):
        self.path = path
        self.root = None

    def load(self):
        self.root = etree.parse(str(self.path))

    def texts(self, rule:str)->list:
        '''return list<str>'''
        # logger.debug(f'xpath texts: {rule}')
        res = [x.replace(u'\xa0', u' ') for x in self.root.xpath(rule)]
        res = [' ' if '' == x else x for x in res]
        logger.debug(res)
        return res

    def pos(self, rule:str)->list:
        '''return list<complex>'''
        logger.debug(rule)
        res = self.texts(rule)
        logger.debug(res)
        points = [str2complex(x) for x in res]
        if len(points) == 1:
            res = points[0]
        else:
            res = points
        logger.debug(res)
        return res

    def content(self, rule:str)->str:
        '''return str'''
        logger.debug(rule)
        # res = self.texts(rule) # list<str>
        # res = ' '.join([" ".join(x.split()) for x in self.texts(rule)])
        res = ''.join(self.texts(rule))
        logger.debug(res)
        return res

    def options(self, rule:str)->list:
        res = [re.sub(r'\|', '_', x) for x in self.root.xpath(rule)]
        logger.debug(res)
        return res

    def count(self, rule:str)->int:
        '''return int'''
        logger.debug(rule)
        res = self.root.xpath(rule)
        return len(res)

    # def element(self, rule:str)->object:
    #     res = self.root.xpath(rule)
    #     return res



if __name__ == "__main__":
    from argparse import ArgumentParser    
    from pathlib import Path
    logger.debug('running xmler.py')
    parse = ArgumentParser()
    parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str, default='./xuexi/src/xml/reader.xml', help='目标文件路径')
    args = parse.parse_args()

    path = Path(args.filename)
    xm = Xmler(path)
    xm.load()
    txt_pic = r'//node[@resource-id="cn.xuexi.android:id/general_card_title_id"]/@text'
    txt_3pic = r'//node[@class="android.widget.ListView"]/node/node[@class="android.widget.LinearLayout" and @index="0"]/node[@class="android.widget.TextView"]/@text'
    txt = r'//node[@class="android.widget.ListView"]/node/node[@class="android.widget.LinearLayout" and @index="0"]/node[@class="android.widget.LinearLayout"]/node[1]/@text'
    for rule in [txt, txt_pic]:
        print(rule)
        items = xm.texts(rule)
        for item in items:
            print(item)