@echo off
cd /d "%~dp0"
for /f %%v in ('py -3 -c "import version;print(version.__version__)"') do set VER=%%v
py -3 -m pip install --user pyinstaller -r requirements.txt
if not exist build_tmp mkdir build_tmp
rem Name, version, company and copyright shown in the exe's Properties - Details.
py -3 exe_info.py build_tmp\exe_info.txt
py -3 -m PyInstaller --noconfirm --clean --onefile --windowed --name Wallwike --icon "%~dp0wallwike.ico" --version-file "%~dp0build_tmp\exe_info.txt" --hidden-import pystray._win32 --distpath "build %VER%" --workpath build_tmp --specpath build_tmp wallwike.py
echo.
if exist "build %VER%\Wallwike.exe" (echo Built: %~dp0build %VER%\Wallwike.exe) else (echo BUILD FAILED - see messages above)
pause
