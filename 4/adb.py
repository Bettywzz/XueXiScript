import time
import subprocess
import random

i = 0
sleep_time = 8 
subprocess.Popen('adb shell input tap 540 1900', shell=True)
time.sleep(sleep_time)
subprocess.Popen('adb shell input tap 431 191', shell=True)
time.sleep(10)
subprocess.Popen('adb shell input swipe 500 1750 500 80', shell=True)
time.sleep(sleep_time)
subprocess.Popen('adb shell input swipe 500 1750 500 80', shell=True)
time.sleep(sleep_time)

# 看6片文章，每篇2min
for i in range(9):
  subprocess.Popen('adb shell input tap 500 ' + str(392 + 400 * (i % 3)), shell=True)
  time.sleep(sleep_time)

  count = 60
  if i > 1:
    count = 6
  for j in range(70):
    if j % 2 and j < 10:
      subprocess.Popen('adb shell input tap 500 850', shell=True)
    time.sleep(1)
    subprocess.Popen('adb shell input swipe 500 1000 500 850', shell=True)
    time.sleep(1)
  # 收藏
  subprocess.Popen('adb shell input tap 923 1872', shell=True)
  time.sleep(2)


#  进入视频

subprocess.Popen('adb shell input tap 753 1896', shell=True)
time.sleep(sleep_time)
subprocess.Popen('adb shell input tap 426 188', shell=True)
time.sleep(10)
subprocess.Popen('adb shell input swipe 500 1000 500 700', shell=True)
time.sleep(sleep_time)

# 看6个视频
for i in range(7):
  subprocess.Popen('adb shell input tap 500 ' + str(370 + 160 * (i)), shell=True)
  time.sleep(sleep_time)
  if i == 0: 
    time.sleep(1830)
  else:
    # for j in range(8):
    #   subprocess.Popen('adb shell input swipe 270 377 320 377', shell=True)
    #   time.sleep(30)
    time.sleep(240)
  subprocess.Popen('adb shell input keyevent KEYCODE_BACK', shell=True)
  time.sleep(sleep_time)
#  if i == 2 or i == 4: 
#    subprocess.Popen('adb shell input swipe 500 1500 500 800', shell=True)
#    time.sleep(sleep_time)

time.sleep(sleep_time)
