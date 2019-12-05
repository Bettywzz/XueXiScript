#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: StudyEveryday
@file: common.py
@author: kessil
@contact: https://github.com/kessil/StudyEveryday/
@time: 2019-07-30(星期二) 20:31
@Copyright © 2019. All rights reserved.
'''
import re
import subprocess
from time import sleep
from pathlib import Path
from .. import logger


class Adble(object):
    def __init__(self, path=Path('./ui.xml'), is_virtual:bool=True, host='127.0.0.1', port=7555):
        # subprocess.Popen(f'adb version', shell=True)
        self.path = path
        self.is_virtual = is_virtual
        self.host = host
        self.port = port
        if self.is_virtual:
            self._connect()          
        else:
            logger.info(f'请确保安卓手机连接手机并打开USB调试!')
        self.device = self._getDevice()
        if self.device is not None:
            logger.info(f'当前设备 {self.device}')
            self.ime = self._getIME()
            self.wmsize = self._size()
            self._setIME('com.android.adbkeyboard/.AdbIME')
        else:
            logger.debug(f'未连接设备')
            raise RuntimeError(f'未连接任何设备')

    def _connect(self):
        '''连接模拟器adb connect host:port'''
        logger.debug(f'正在连接模拟器{self.host}:{self.port}')
        subprocess.check_call(f'adb connect {self.host}:{self.port}', shell=True, stdout=subprocess.PIPE)

        
    def _disconnect(self):
        '''连接模拟器adb connect host:port'''
        logger.debug(f'正在断开模拟器{self.host}:{self.port}')
        if 0 == subprocess.check_call(f'adb disconnect {self.host}:{self.port}', shell=True, stdout=subprocess.PIPE):
            logger.info(f'断开模拟器{self.host}:{self.port} 成功')
        else:
            logger.info(f'断开模拟器{self.host}:{self.port} 失败')

    def draw(self, orientation='down', distance=100, duration=500):
        height, width = max(self.wmsize), min(self.wmsize) # example: [1024, 576]
        # 中点 三分之一点 三分之二点
        x0, x1, x2 = width//2, width//3, width//3*2 
        y0, y1, y2 = height//2, height//3, height//3*2
        if 'down' == orientation:
            self.swipe(x0, y1, x0, y1+distance, duration)
        elif 'up' == orientation:
            self.swipe(x0, y2, x0, y2-distance, duration)
        elif 'left' == orientation:
            self.swipe(x2, y0, x2-distance, y0, duration)
        elif 'right' == orientation:
            self.swipe(x1, y0, x1+distance, y0, duration)
        else:
            logger.debug(f'没有这个方向 {orientation} 无法划动')
        return 0
    
    def _size(self):
        res = subprocess.check_output(f'adb -s {self.device} shell wm size', shell=False)
        if isinstance(res, bytes):
            wmsize = re.findall(r'\d+', str(res, 'utf-8'))
        else:
            wmsize = re.findall(r'\d+', res)
        logger.debug(f'屏幕分辨率：{wmsize}')
        res = [int(x) for x in wmsize]
        return res
    

    def _setIME(self, ime):
        logger.debug(f'设置输入法 {ime}')
        logger.debug(f'正在设置输入法 {ime}')
        if 0 == subprocess.check_call(f'adb -s {self.device} shell ime set {ime}', shell=True, stdout=subprocess.PIPE):
            logger.debug(f'设置输入法 {ime} 成功')
        else:
            logger.debug(f'设置输入法 {ime} 失败')

    def _getIME(self)->list:
        logger.debug(f'获取系统输入法list')
        res = subprocess.check_output(f'adb -s {self.device} shell ime list -s', shell=False)
        if isinstance(res, bytes):
            # ime = re.findall(r'\d+', str(res, 'utf-8'))
            ime = re.findall(r'\S+', str(res, 'utf-8'))
        else:
            ime = re.findall('\S+', res)
        logger.debug(f'系统输入法：{ime}')
        return ime[0]

    def _getDevice(self)->str:
        logger.debug(f'获取连接的设备信息')
        res = subprocess.check_output(f'adb devices')
        if isinstance(res, bytes):
            res = str(res, 'utf-8')
        devices = re.findall(r'(.*)\tdevice', res)
        logger.debug(f'已连接设备 {devices}')
        if self.is_virtual and f'{self.host}:{self.port}' in devices:
            return f'{self.host}:{self.port}'
        elif 0 == len(devices):
            return None
        else:
            return devices[0]

        

    def uiautomator(self, path=None, filesize=10240):
        if not path:
            path = self.path
        for i in range(3):
            if path.exists():
                path.unlink()
            else:
                logger.debug('文件不存在,无需删除')
            subprocess.check_call(f'adb -s {self.device} shell uiautomator dump /sdcard/ui.xml', shell=True, stdout=subprocess.PIPE)
            # sleep(1)
            subprocess.check_call(f'adb -s {self.device} pull /sdcard/ui.xml {path}', shell=True, stdout=subprocess.PIPE)
            if filesize < path.stat().st_size:
                break
            else:
                sleep(1)

    def screenshot(self, path=None):
        if not path:
            path = self.path
        subprocess.check_call(f'adb -s {self.device} shell screencap -p /sdcard/ui.png', shell=True, stdout=subprocess.PIPE)
        # sleep(1)
        subprocess.check_call(f'adb -s {self.device} pull /sdcard/ui.png {path}', shell=True, stdout=subprocess.PIPE)

    def swipe(self, sx, sy, dx, dy, duration):
        ''' swipe from (sx, xy) to (dx, dy) in duration ms'''
        # adb shell input swipe 500 500 500 200 500
        logger.debug(f'滑动操作 ({sx}, {sy}) --{duration}ms-> ({dx}, {dy})')
        res = subprocess.check_call(f'adb -s {self.device} shell input swipe {sx} {sy} {dx} {dy} {duration}', shell=True, stdout=subprocess.PIPE)
        # sleep(1)
        return res

    def slide(self, begin, end, duration=500):
        '''接收complex参数坐标'''
        logger.debug(f'滑动操作 {begin} --{duration}ms-> {end}')
        sx, sy = int(begin.real), int(begin.imag)
        dx, dy = int(end.real), int(end.imag)
        res = subprocess.check_call(f'adb -s {self.device} shell input swipe {sx} {sy} {dx} {dy} {duration}', shell=True, stdout=subprocess.PIPE)
        # sleep(1)
        return res


    def tap(self, x, y=None, duration=50):
        # subprocess.check_call(f'adb shell input tap {x} {y}', shell=True, stdout=subprocess.PIPE)
        '''改进tap为长按50ms，避免单击失灵'''
        if y is not None:
            if isinstance(x, int) and isinstance(y, int):
                dx, dy = int(x), int(y)
            else:
                logger.debug(f'输入坐标有误')
        else:
            try:
                dx, dy = int(x.real), int(x.imag)
            except Exception as e:
                raise AttributeError(f'{x} 不是可点击的坐标')
        logger.debug(f'触摸操作 ({dx}, {dy})')
        return self.swipe(dx, dy, dx, dy, duration)

    def back(self):
        # adb shell input keyevent 4 
        logger.debug(f'adb 触发<返回按钮>事件')
        subprocess.check_call(f'adb -s {self.device} shell input keyevent 4', shell=True, stdout=subprocess.PIPE)


    def input(self, msg):
        logger.debug(f'输入文本 {msg}')
        # subprocess.check_call(f'adb shell input text {msg}', shell=True, stdout=subprocess.PIPE)
        subprocess.check_call(f'adb -s {self.device} shell am broadcast -a ADB_INPUT_TEXT --es msg {msg}', shell=True, stdout=subprocess.PIPE)

    def close(self):
        self._setIME(self.ime)
        if self.is_virtual:
            self._disconnect()

if __name__ == "__main__":
    from argparse import ArgumentParser
    logger.debug('running adble.py')
    parse = ArgumentParser()
    parse.add_argument(dest='filename', metavar='filename', nargs="?", type=str, help='目标文件路径')
    parse.add_argument('-s', '--screenshot', metavar='screenshot', nargs='?', const=True, type=bool, default=False, help='截图并上传')
    parse.add_argument('-t', '--text', metavar='text', type=str, default='adb input text test', help='输入文字')
    parse.add_argument('-u', '--uiautomator', metavar='uiautomator', nargs='?', const=True, type=bool, default=False, help='解析布局xml并上传')
    parse.add_argument('-v', '--virtual', metavar='virtual', nargs='?', const=True, type=bool, default=False, help='是否模拟器')
    args = parse.parse_args()
    adb = Adble(f'noname', args.virtual)
    if args.filename:
        path = Path(args.filename)
        if args.screenshot:
            adb.screenshot(path.with_suffix('.png'))
            print(f'截图保存成功')
        if args.uiautomator:
            # sleep(2)
            adb.uiautomator(path.with_suffix('.xml'))
            print(f'布局保存成功')
    else:
        # print(type(adb.device), adb.device)
        adb.input(args.text)
        print(f'输入文字{args.text}')

    adb.close()

    
