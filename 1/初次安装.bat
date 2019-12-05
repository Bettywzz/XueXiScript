@echo off
cd /d %~dp0
echo install venv...
python -m venv venv
echo venv installed OK.
echo install packages
venv\scripts\python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo packages installed OK.
pause