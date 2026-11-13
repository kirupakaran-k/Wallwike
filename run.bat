@echo off
cd /d "%~dp0"
where pyw >nul 2>nul && (start "" pyw -3 spanpaper.py) || (start "" pythonw spanpaper.py)
