#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
@project: AutoXue
@file: __init__.py
@author: kessil
@contact: https://github.com/kessil/AutoXue/
@time: 2019-10-26(星期六) 09:03
@Copyright © 2019. All rights reserved.
'''
import re
import time
import requests
import string
import subprocess
from urllib.parse import quote
from collections import defaultdict
from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .unit import Timer, logger, caps, rules, cfg
from .model import BankQuery
from xuexi import SecureRandom

class Automation():
    # 初始化 Appium 基本参数
    def __init__(self):
        self.connect()
        self.desired_caps = {
            "platformName": caps["platformname"],
            "platformVersion": caps["platformversion"],
            "automationName": caps["automationname"],
            "unicodeKeyboard": caps["unicodekeyboard"],
            "resetKeyboard": caps["resetkeyboard"],
            "noReset": caps["noreset"],
            'newCommandTimeout': 800,
            "deviceName": caps["devicename"],
            "uuid": caps["uuid"],
            "appPackage": caps["apppackage"],
            "appActivity": caps["appactivity"]
        }
        logger.info('打开 appium 服务,正在配置...')
        self.driver = webdriver.Remote('http://localhost:4723/wd/hub', self.desired_caps)
        self.wait = WebDriverWait(self.driver, 10)
        self.size = self.driver.get_window_size()

    def connect(self):
        logger.info(f'正在连接模拟器 {caps["uuid"]}，请稍候...')
        if 0 == subprocess.check_call(f'adb connect {caps["uuid"]}', shell=True, stdout=subprocess.PIPE):
            logger.info(f'模拟器 {caps["uuid"]} 连接成功')
        else:
            logger.info(f'模拟器 {caps["uuid"]} 连接失败')

    def disconnect(self):
        logger.info(f'正在断开模拟器 {caps["uuid"]}，请稍候...')
        if 0 == subprocess.check_call(f'adb disconnect {caps["uuid"]}', shell=True, stdout=subprocess.PIPE):
            logger.info(f'模拟器 {caps["uuid"]} 断开成功')
        else:
            logger.info(f'模拟器 {caps["uuid"]} 断开失败')

    # 屏幕方法
    def swipe_up(self):
        # 向上滑动屏幕
        self.driver.swipe(self.size['width'] * SecureRandom.uniform(0.55, 0.65),
                          self.size['height'] * SecureRandom.uniform(0.65, 0.75),
                          self.size['width'] * SecureRandom.uniform(0.55, 0.65),
                          self.size['height'] * SecureRandom.uniform(0.25, 0.35), SecureRandom.uniform(800, 1200))
        logger.debug('向上滑动屏幕')

    def swipe_down(self):
        # 向下滑动屏幕
        self.driver.swipe(self.size['width'] * SecureRandom.uniform(0.55, 0.65),
                          self.size['height'] * SecureRandom.uniform(0.25, 0.35),
                          self.size['width'] * SecureRandom.uniform(0.55, 0.65),
                          self.size['height'] * SecureRandom.uniform(0.65, 0.75), SecureRandom.uniform(800, 1200))
        logger.debug('向下滑动屏幕')

    def swipe_right(self):
        # 向右滑动屏幕
        self.driver.swipe(self.size['width'] * SecureRandom.uniform(0.01, 0.11),
                          self.size['height'] * SecureRandom.uniform(0.75, 0.89),
                          self.size['width'] * SecureRandom.uniform(0.89, 0.98),
                          self.size['height'] * SecureRandom.uniform(0.75, 0.89), SecureRandom.uniform(800, 1200))
        logger.debug('向右滑动屏幕')
    def swipe_left(self):
        # 向右滑动屏幕
        self.driver.swipe(self.size['width'] * SecureRandom.uniform(0.89, 0.98),
                          self.size['height'] * SecureRandom.uniform(0.75, 0.89),
                          self.size['width'] * SecureRandom.uniform(0.01, 0.11),
                          self.size['height'] * SecureRandom.uniform(0.75, 0.89), SecureRandom.uniform(800, 1200))
        logger.debug('向左滑动屏幕')

    # 返回事件
    def safe_back(self, msg='default msg'):
        logger.debug(msg)
        self.driver.keyevent(4)
        time.sleep(1)

    def safe_click(self, ele:str):
        self.wait.until(EC.presence_of_element_located((By.XPATH, ele))).click()
        time.sleep(1)

    def __del__(self):
        self.driver.close_app()
        self.driver.quit()


class App(Automation):
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
        }
        self.query = BankQuery()
        self.bank = None
        self.score = defaultdict(tuple)

        super().__init__()
        self.driver.wait_activity('com.alibaba.android.rimet.biz.home.activity.HomeActivity', 20, 3)
        self.view_score()
        self._challenge_init()


    def view_score(self):
        self.safe_click(rules['score_entry'])
        titles = ["登录", "阅读文章", "视听学习", "文章学习时长", 
                "视听学习时长", "每日答题", "每周答题", "专项答题", 
                "挑战答题", "订阅", "收藏", "分享", "发表观点"]
        score_list = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, rules['score_list'])))
        for t, score in zip(titles, score_list):
            s = score.get_attribute("name")
            self.score[t] = tuple([int(x) for x in re.findall(r'\d+', s)])

        # print(self.score)
        for i in self.score:
            logger.debug(f'{i}, {self.score[i]}')
        self.safe_back('score -> home')

    def back_or_not(self, title):
        # return False
        g, t = self.score[title]
        if g == t:
            logger.debug(f'{title} 积分已达成，无需重复获取积分')
            return True
        return False

    def _search(self, content, options, exclude=''):
        logger.debug(f'搜索 {content} <exclude = {exclude}>')
        logger.info(f"选项 {options}")
        content = re.sub(r'[\(（]出题单位.*', "", content)
        if options[-1].startswith("以上") and chr(len(options)+64) not in exclude:
            logger.info(f'根据经验: {chr(len(options)+64)} 很可能是正确答案')
            return chr(len(options)+64)
        # url = quote('https://www.baidu.com/s?wd=' + content, safe=string.printable)
        url = quote("https://www.sogou.com/web?query=" + content, safe=string.printable)
        response = requests.get(url, headers=self.headers).text
        counts = []
        for i, option in zip(['A', 'B', 'C', 'D', 'E', 'F'], options):
            count = response.count(option)
            counts.append((count, i))
            logger.info(f'{i}. {option}: {count} 次')
        counts = sorted(counts, key=lambda x:x[0], reverse=True)
        counts = [x for x in counts if x[1] not in exclude]
        c, i = counts[0]
        # 降序排列第一个为计数最大值
        if 0 == c:     
            # 替换了百度引擎为搜狗引擎，结果全为零的机会应该会大幅降低       
            _, i = SecureRandom.choice(counts)
            logger.info(f'搜索结果全0，随机一个 {i}')

        logger.info(f'根据搜索结果: {i} 很可能是正确答案')
        return i

    def _verify(self, category, content, options):
        logger.debug(f'{category} {content} {options}')
        self.bank = self.query.get({
            "category": category,
            "content": content,
            "options": options
        })
        # logger.info(options)
        if self.bank and self.bank["answer"]:
            logger.info(f'已知的正确答案: {self.bank["answer"]}')
            return self.bank["answer"]
        if "多选题" == category:
            return "ABCDEFG"[:len(options)]
        elif "填空题" == category:
            return None # ''.join(random.sample(string.ascii_letters + string.digits, 8))
        else:
            if self.bank and self.bank["excludes"]:
                logger.info(f'已知的排除项有: {self.bank["excludes"]}')
                return self._search(content, options, self.bank["excludes"])
            return self._search(content, options)

    def _update_bank(self, item):
        if not self.bank or not self.bank["answer"]:
            self.query.put(item)

# 挑战答题模块
# class Challenge(App):
    def _challenge_init(self):
        # super().__init__()
        try:
            self.challenge_count = cfg.getint('prefers', 'challenge_count')
        except:
            g, t = self.score["挑战答题"]
            if t == g:
                self.challenge_count = 0
            else:
                self.challenge_count = SecureRandom.randint(
                        cfg.getint('prefers', 'challenge_count_min'), 
                        cfg.getint('prefers', 'challenge_count_max'))

        self.delay_bot = cfg.getint('prefers', 'challenge_delay_min')
        self.delay_top = cfg.getint('prefers', 'challenge_delay_max')

    def _challenge_cycle(self, num):
        self.safe_click(rules['challenge_entry'])
        while num:
            content = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, rules['challenge_content']))).get_attribute("name")
            option_elements = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, rules['challenge_options'])))
            options = [x.get_attribute("name") for x in option_elements]
            length_of_options = len(options)
            logger.info(f'<{num}> {content}')
            answer = self._verify(category='单选题', content=content, options=options)
            delay_time = SecureRandom.randint(self.delay_bot, self.delay_top)
            logger.info(f'随机延时 {delay_time} 秒提交答案: {answer}')
            time.sleep(delay_time)
            option_elements[ord(answer)-65].click()
            try:
                time.sleep(2)
                wrong = self.driver.find_element_by_xpath(rules['challenge_revival'])
                logger.debug(f'很遗憾回答错误')
                self._update_bank({
                        "category": "单选题",
                        "content": content,
                        "options": options,
                        "answer": "",
                        "excludes": answer,
                        "notes": ""
                    })
                break
            except:
                logger.debug(f'回答正确')
                num -= 1            
                self._update_bank({
                    "category": "单选题",
                    "content": content,
                    "options": options,
                    "answer": answer,
                    "excludes": "",
                    "notes": ""
                })
        else:
            logger.info(f'已完成指定题量, 本题故意答错后自动退出，否则延时30秒等待死亡')
            content = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, rules['challenge_content']))).get_attribute("name")
            option_elements = self.wait.until(EC.presence_of_all_elements_located(
                (By.XPATH, rules['challenge_options'])))
            options = [x.get_attribute("name") for x in option_elements]
            length_of_options = len(options)
            logger.info(f'<{num}> {content}')
            answer = self._verify(category='单选题', content=content, options=options)
            final_choose = ((ord(answer)-65)+SecureRandom.randint(1,length_of_options))%length_of_options
            delay_time = SecureRandom.randint(self.delay_bot, self.delay_top)
            logger.info(f'随机延时 {delay_time} 秒提交答案: {chr(final_choose+65)}')
            time.sleep(delay_time)
            option_elements[final_choose].click()
            time.sleep(2)
            try:
                wrong = self.driver.find_element_by_xpath(rules['challenge_revival'])
                logger.debug(f'恭喜回答错误')
            except:
                logger.debug('抱歉回答正确')
                time.sleep(30)
        self.safe_back('challenge -> quiz')
        return num


    def _challenge(self):
        logger.info(f'挑战答题 目标 {self.challenge_count} 题, Go!')
        while True:
            result = self._challenge_cycle(self.challenge_count)
            if 0 >= result:
                logger.info(f'已成功挑战 {self.challenge_count} 题，正在返回')
                break
            else:
                delay_time = SecureRandom.randint(5,10)
                logger.info(f'本次挑战 {self.challenge_count - result} 题，{delay_time} 秒后再来一组')
                time.sleep(delay_time)
                continue

        

    def challenge(self):
        if 0 == self.challenge_count:
            logger.info(f'挑战答题积分已达成，无需重复挑战')
            return
        self.safe_click(rules['mine_entry'])
        self.safe_click(rules['quiz_entry'])
        self._challenge()
        self.safe_back('quiz -> mine')
        self.safe_back('mine -> home')
