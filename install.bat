@echo off
cd /d "%~dp0"
py -3 -m pip install --user -r requirements.txt || python -m pip install --user -r requirements.txt
echo.
echo Checking image sources...
py -3 wallwike.py --test || python wallwike.py --test
pause
