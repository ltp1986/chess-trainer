@echo off
echo ==========================================
echo 象棋自动复盘系统 - 打包脚本
echo ==========================================
echo.

REM 检查PyInstaller是否安装
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)

echo.
echo 开始打包...
echo.

cd /d "%~dp0"
pyinstaller --onefile --noconsole --name "象棋复盘系统" --icon=NONE --clean src/chess_analyzer.py

echo.
echo ==========================================
echo 打包完成！
echo EXE文件位于: dist\象棋复盘系统.exe
echo ==========================================
pause
