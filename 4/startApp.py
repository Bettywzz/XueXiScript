from appium import webdriver
import time

desired_caps = {}
desired_caps['platformName'] = 'Android' #android的apk还是IOS的ipa
desired_caps['platformVersion'] = '5.1.1' #android系统的版本号
desired_caps['deviceName'] = 'HUAWEI_MLA_AL10' #手机设备名称，通过adb devices 查看
desired_caps['appPackage'] = 'cn.xuexi.android' #apk的包名
desired_caps['appActivity'] = 'com.alibaba.android.rimet.biz.SplashActivity' #apk的launcherActivity
desired_caps['unicodeKeyboard'] = True #使用unicodeKeyboard的编码方式来发送字符串
desired_caps['resetKeyboard'] = True #将键盘给隐藏起来
desired_caps['noReset'] = True   #启动app的时候不会清app数据
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
time.sleep(10)