@echo off
echo ==========================================
echo 象棋自动复盘系统
echo ==========================================
echo.

cd /d "%~dp0"src"
python chess_analyzer.py

pause
