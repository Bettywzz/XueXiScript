#!/usr/bin/env python
# -*- coding:utf-8 -*-

from argparse import ArgumentParser
import time
from . import App
from .unit import logger
from .secureRandom import SecureRandom as random
import sys

parse = ArgumentParser(description="Accept username and password if necessary!")

parse.add_argument("-u", "--username", metavar="username", type=str, default='', help='User Name')
parse.add_argument("-p", "--password", metavar="password", type=str, default='', help='Pass Word')
args = parse.parse_args()
app = App(args.username, args.password)

def shuffle(funcs):
    random.shuffle(funcs)
    for func in funcs:
        func()
        time.sleep(5)

def start():
    if random.random() > 0.5:
        logger.debug(f'视听学习优先')
        app.watch()
        app.music()
        shuffle([app.read, app.daily, app.challenge, app.weekly])
    else:
        logger.debug(f'视听学习置后')
        app.music()
        shuffle([app.read, app.daily, app.challenge, app.weekly])
        app.watch()
    app.logout_or_not()
    
    sys.exit(0)

def test():
    app.weekly()
    logger.info(f'测试完毕')

if __name__ == "__main__":
    start()
    # test()