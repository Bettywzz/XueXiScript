#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: manage.py
@author: kessil
@contact: https://github.com/kessil/AutoXue/
@time: 2019-08-17(星期六) 13:25
@Copyright © 2019. All rights reserved.
'''

from argparse import ArgumentParser

parse = ArgumentParser()
parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str, help='目标文件路径')
parse.add_argument('-a', '--article', metavar='article', nargs='?', const=True, type=bool, default=False, help='是否完成阅读文章')
parse.add_argument('-b', '--behavior', metavar='behavior', type=str, default='download', help='数据库操作，upload、download')
parse.add_argument('-c', '--challenge', metavar='challenge', nargs='?', const=True, type=bool, default=False, help='是否完成挑战答题')
parse.add_argument('-d', '--daily', metavar='daily', nargs='?', const=True, type=bool, default=False, help='是否完成每日答题')
parse.add_argument('-v', '--video', metavar='video', nargs='?', const=True, type=bool, default=False, help='是否完成视听学习')
parse.add_argument('-u', '--uri', metavar='uri', type=str, default='database_uri', help='数据库选择: database_uri、database_challenge、database_daily')

args = parse.parse_args()

if args.filename:
    from . import cfg
    from .model import Model
    db = Model(cfg.get('common', args.uri))
    if 'upload' == args.behavior:
        db.upload(args.filename)
    elif 'download' == args.behavior:
        db.download(args.filename)
    else:
        pass
elif any([args.article, args.video, args.daily, args.challenge]):
    print(f'\n\t阅读文章{("[×]", "[√]")[args.article]}\t视听学习{("[×]", "[√]")[args.video]}\t每日答题{("[×]", "[√]")[args.daily]}\t挑战答题{("[×]", "[√]")[args.challenge]}\n')
    from . import App
    app = App()
    app.start(args.article, args.video, args.daily, args.challenge)
else:
    print(f'请根据需要选择执行相应操作，-a -c -d -v 按需添加')

