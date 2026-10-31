@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem 统一使用 Python 3.12（D:\py312）。3.14 已弃用：ML 生态普遍还没有 3.14 的轮子。
set PY=D:\py312\python\python.exe
if not exist "%PY%" set PY=python
echo ==========================================================
echo  直播中控台
echo  控制台 : http://127.0.0.1:8777
echo  提词器 : http://127.0.0.1:8777/teleprompter
echo  (关闭此窗口即停止服务)
echo ==========================================================
start "" http://127.0.0.1:8777
"%PY%" "console\server.py"
pause
