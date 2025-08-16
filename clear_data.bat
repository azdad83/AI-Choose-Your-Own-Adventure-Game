@echo off
REM Clear Game Data - Windows Batch Script
REM =======================================
REM This script activates the virtual environment and runs the clear_game_data.py script

echo.
echo Choose Your Own Adventure - Clear Game Data
echo ===========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run this script from the game directory.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment and run the cleaner script
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Running game data cleaner...
echo.

python clear_game_data.py

echo.
echo Script completed.
pause