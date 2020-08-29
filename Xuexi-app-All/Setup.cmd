::使用UTF-8编码，请用Notepad类软件进行更改，否则中文会乱码！


@echo off
chcp 65001
title=Setup

cd /d %~dp0
echo %cd%
echo First, Confirm Python3.7+ Installed?
echo install venv...
python -m venv venv
echo venv installed OK.
echo install packages...
REM venv\scripts\python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\scripts\python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\scripts\python -m pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\scripts\python -m pip install Appium-Python-Client -i https://pypi.tuna.tsinghua.edu.cn/simple
echo Packages Installed OK.

pause