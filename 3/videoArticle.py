"""
info:
author:Mrmeng
github:https://github.com/Mrmeng-bat/
update_time:2019-3-24
"""
import os
import subprocess
from appium import webdriver
import time
import numpy as np
import random

#已读文章或视频列表
all_of_text_list = np.load ("text_db.npy").tolist()
all_of_vod_list = np.load ("move_db.npy").tolist()

#动作间隔的随机数
series = [2,3,4,5,6,7,8,9,10,11,12]
#观看视频的随机数
vod_series= [380,390,400,410,420]

def init_driver():   #return desired_caps字典
    desired_caps = {}
    desired_caps['platformName'] = 'Android'
    desired_caps['platformVersion'] = '5.1.1'
    desired_caps['deviceName'] = 'HUAWEI_MLA_AL10'
    desired_caps['appPackage'] = 'cn.xuexi.android'
    desired_caps['appActivity'] = 'com.alibaba.android.rimet.biz.SplashActivity'
    desired_caps['noSign'] = True
    desired_caps['noReset'] = True
    desired_caps['newCommandTimeout'] = 3600
    return desired_caps

def swipe_y(driver): #y下滑动作
    y = driver.get_window_size()['height']
    driver.swipe(0, 5/10*y, 0, 2/10*y, 200)

def swipe_y2(driver): #y下滑动作
    y = driver.get_window_size()['height']
    for i in range(2):
        for j in range (30):
            driver.swipe(0, 3/10*y, 0, 2/10*y, 500)
            time.sleep (3)

def swipe_x(driver): #x下滑动作
    x = driver.get_window_size()['width']
    driver.swipe(2/10*x, 0, 6/10*x, 0, 200)

def move_to_index(driver): #转到我的学习
	driver.tap([(505,1828), (575,1898)], 500)
    #driver.find_element_by_id("cn.xuexi.android:id/home_bottom_tab_icon_large").click()

def move_to_vedio(driver): #转到电视台
	driver.tap([(732,1828), (780,1876)], 500)
	#driver.find_element_by_xpath('//android.widget.TextView[@text="电视台"]').click()

def move_to_vod(driver):
    driver.find_element_by_xpath('//android.widget.TextView[@text="视听学习"]').click()

# 点击首页的“传播中国”
def move_to_other_vod(driver):
    driver.find_element_by_id("cn.xuexi.android:id/home_bottom_tab_icon_large").click()
    driver.find_element_by_xpath('//android.widget.TextView[@text="传播中国"]').click()

def move_to_my_study(driver):
    driver.find_element_by_xpath('//android.widget.TextView[@text="我的"]').click()

# 点击首页的“时评”
def move_to_shi_ping(driver):
    driver.find_element_by_id("cn.xuexi.android:id/home_bottom_tab_icon_large").click()
    driver.find_element_by_xpath('//android.widget.TextView[@text="时评"]').click()

# 点击收藏文章
def click_collect(driver):
	driver.tap([(876,1852), (972,1900)], 500)

# 点击分享文章
def click_share(driver):	
	driver.tap([(972,1852), (1044,1900)], 500)
	driver.tap([(71,1291), (199,1419)], 500)
	driver.tap([(24,565), (120,661)], 500)
	driver.find_element_by_id("android:id/button1").click()
		
# 返回上一级
def back_to_previous(driver):
    driver.back()

def get_text_list(driver):   #返回未读文章列表
    text_list = []
    lists = driver.find_elements_by_class_name ('android.widget.TextView')
    for d_text in lists:
        if len(text_list) >6:
            break
        if len(d_text.text)<11:
            continue
        if d_text.text not in  all_of_text_list :
            all_of_text_list.append(d_text.text )
            text_list.append(d_text)
            #print("找到未读文章：",d_text.text)
    return text_list

def get_vod_list(driver):   #返回未看视频列表
    vod_list = []
    lists = driver.find_elements_by_id('cn.xuexi.android:id/general_card_title_id')
    for d_vod in lists:
        if len(vod_list) >6:
            break
        if d_vod.text not in  all_of_vod_list:
            all_of_vod_list.append(d_vod.text )
            vod_list.append(d_vod )
            #print("找到未看视频：",d_vod.text)
    return vod_list

def look_text(driver):
	lists=[]
	textNum = 6 + random.choice([0,1,2])
	time.sleep(2)
	move_to_shi_ping(driver)
	time.sleep(2)
	print("开始文章学习,随机看：",textNum,'个')
	while len(lists)<textNum:
		time.sleep(2)
		for_list = get_text_list(driver)
		for d_text in for_list:
			if len(lists)>textNum:
				break
			lists.append(d_text.text)
			print('第',len(lists),"篇文章: ",d_text.text)
			d_text.click()
			time.sleep(2)
			swipe_y2(driver)
			time.sleep(30+random.choice(series))
			swipe_x(driver)
			time.sleep(2)
			if len(lists)<3:
				click_share(driver)
				time.sleep(2)
				click_collect(driver)
				print("成功收藏并分享文章")
			if len(lists)>0:
				back_to_previous(driver)
		swipe_y(driver)
	# print("文章学习完成")
	text_list = np.array (all_of_text_list)
	np.save ('text_db.npy',text_list)
    
def look_vod(driver):   
    lists=[]
    vodNum = 6 + random.choice([1,2,3])
    print('开始视频学习,随机看：',vodNum,'个')
    time.sleep(2)
    move_to_vedio(driver)
    #move_to_other_vod(driver)
    time.sleep(2)
    while len(lists)<vodNum:
        time.sleep(2)
        for_list = get_vod_list(driver)
        for d_text in for_list:
            if len(lists)>vodNum:
                break 
            lists.append(d_text.text)
            print('第',len(lists),"个视频: ",d_text.text)
            d_text.click()
            time.sleep(2)
            swipe_y(driver)
            time.sleep(250+random.choice(series))
            swipe_x(driver)
            time.sleep(2)
            if len(lists)>0:
            	back_to_previous(driver)
        swipe_y(driver)
    # print("视频学习完成")
    move_list = np.array (all_of_vod_list)
    np.save ('move_db.npy',move_list)

# 百灵开始看
def easy_vod(driver):
	vodTime = random.choice(vod_series)+random.choice(series)
	driver.find_element_by_xpath('//android.widget.TextView[@text="百灵"]').click()
	time.sleep(5)
	print('开始视频学习,随机看：',vodTime,'s')
	driver.tap([(500,500), (600,600)], 500)
	time.sleep(vodTime)

def print_log():
    print("等待任务执行")

def job():
    # print('正在打开夜神模拟器')
    # os.popen( r'D:\Nox\bin\Nox.exe launch -name:夜神模拟器')
    # print("正在打开appium")
    # res = subprocess.Popen('appium', shell=True)
    # time.sleep(10)
    driver = webdriver.Remote('http://localhost:4723/wd/hub', init_driver())
    print_log()
    time.sleep(10)
    look_text(driver)
    move_to_index(driver)
    #easy_vod(driver)    
    look_vod(driver)
    driver.quit()
    print("文章视频任务完成")
    # print("正在关闭夜神模拟器")
    # os.popen (r"D:\Nox\bin\Nox.exe quit -index:0 ")
    # time.sleep(5)
    
if __name__ == '__main__':
    job()

