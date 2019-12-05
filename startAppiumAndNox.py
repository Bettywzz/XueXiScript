import time
import win32gui
import win32ui
import win32api
import win32con
import subprocess
import os

#查找游戏窗口，返回窗口起始坐标
def find_flash_window():
    hwnd = win32gui.FindWindow(None, "Appium")
    if(hwnd):
        rect = win32gui.GetWindowRect(hwnd)
        return rect[0],rect[1]
    return None
 
# 鼠标左键点击屏幕上的坐标(x, y)
def mouse_click(x, y):
    # 鼠标定位到坐标(x, y)
    win32api.SetCursorPos([x, y])
     # 鼠标左键按下
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    # 鼠标左键弹起
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    print("打开Appium服务器")
           
#程序入口
#print("正在查找Appium窗口")
os.popen( r'D:\Nox\bin\Nox.exe launch -name:夜神模拟器')
#os.popen( r'"C:\Program Files\Appium\Appium.exe" launch -name:Appium')
res = subprocess.Popen('appium', shell=True)
while 1:
    pos = find_flash_window()
    if(pos == None):
        print("Appium 未开启!")
        time.sleep(5)
    else:
        #print("打开Appium")
        time.sleep(5)
        mouse_click(960, 640)
        break
    