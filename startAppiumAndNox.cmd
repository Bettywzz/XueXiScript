@echo off
e:
cd E:\AutoXue

start "" cmd /k call E:\AutoXue\Xuexi-app-All\Core.cmd
::��appium��ҹ��ģ����
::python startAppiumAndNox.py
start appium -a 127.0.0.1 -p 4723
start D:\Nox\bin\Nox.exe 

