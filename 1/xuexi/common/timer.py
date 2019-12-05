#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: quizXue
@file: timer.py
@author: kessil
@contact: https://github.com/kessil/quizXue/
@time: 2019-08-08(星期四) 14:11
@Copyright © 2019. All rights reserved.
'''
import time

class Timer:
    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError(f'Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError(f'Not Started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0
    
    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()