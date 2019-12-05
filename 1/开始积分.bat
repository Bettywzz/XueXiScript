@echo off
cd /d %~dp0
venv\scripts\python -m xuexi -a -c -d -v
pause