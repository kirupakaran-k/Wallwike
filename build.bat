@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Building Wallwike
rem Don't leave __pycache__ folders next to the source files.
set "PYTHONDONTWRITEBYTECODE=1"

rem ---------------------------------------------------------------- where things go
rem The finished app goes in "build <version>" OUTSIDE the version folders:
rem   run from  D:\other\Wallwike\version 1\1.6 - ...\build.bat  ->  D:\other\Wallwike\build 1.6
for %%I in ("%~dp0.") do set "HERE=%%~fI"
set "PARENTNAME=-"
for %%I in ("%HERE%\..") do (
  set "PARENT=%%~fI"
  set "PARENTNAME=%%~nxI"
)
set "ROOT=%HERE%"
if /i "%PARENTNAME:~0,8%"=="version " for %%I in ("%PARENT%\..") do set "ROOT=%%~fI"
rem The build tools live outside your source folder too (reused by every build).
set "ENV=%LOCALAPPDATA%\Wallwike\build-env"

rem ---------------------------------------------------------------- find Python
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY where python >nul 2>nul && set "PY=python"
if not defined PY (
  echo Python 3 was not found.
  echo Install it with:  winget install Python.Python.3.12
  echo or from https://www.python.org/downloads/  then run this file again.
  pause
  exit /b 1
)

rem ---------------------------------------------------------------- 1-2. Python and libraries
echo [1/5] Preparing the build tools...   (started %TIME:~0,8%)
if not exist "%ENV%\Scripts\python.exe" echo       First build on this PC: setting them up in "%ENV%"
if not exist "%ENV%\Scripts\python.exe" %PY% -m venv "%ENV%" || goto :fail
call "%ENV%\Scripts\activate.bat" || goto :fail

echo [2/5] Installing libraries...   (started %TIME:~0,8%)
python -m pip install -r requirements.txt pyinstaller --progress-bar on --disable-pip-version-check --timeout 60 --retries 10 || goto :fail

set "VER="
for /f "delims=" %%v in ('python -c "import version; print(version.VERSION)"') do set "VER=%%v"
if not defined VER (
  echo       Couldn't read the version number from version.py.
  goto :fail
)
set "OUT=%ROOT%\build %VER%"
echo       Wallwike %VER% will be built into "%OUT%"

rem ---------------------------------------------------------------- 3. close the running app
echo [3/5] Closing Wallwike if it's running...   (%TIME:~0,8%)
set "WASRUNNING="
tasklist /FI "IMAGENAME eq Wallwike.exe" /NH 2>nul | find /I "Wallwike.exe" >nul && set "WASRUNNING=1"
if defined WASRUNNING taskkill /F /IM Wallwike.exe >nul 2>nul
if defined WASRUNNING >nul ping -n 3 127.0.0.1

rem ---------------------------------------------------------------- 4. clear old builds
echo [4/5] Clearing out the old build...   (%TIME:~0,8%)
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "%OUT%" rmdir /s /q "%OUT%"
if exist "%OUT%" echo       Couldn't clear "%OUT%". Close anything using it and run this again.
if exist "%OUT%" goto :fail
mkdir "%OUT%" || goto :fail

rem ---------------------------------------------------------------- 5. build
echo [5/5] Building Wallwike.exe (a minute or two)...   (started %TIME:~0,8%)
echo       The steps are saved to build.log. This is quiet while it works; that's normal.
python wallwike.py --make-icon "%OUT%\wallwike.ico" >nul 2>nul || goto :fail
rem Name, version, company and copyright shown in the exe's Properties - Details.
python exe_info.py "%OUT%\exe_info.txt" || goto :fail
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Wallwike --hidden-import pystray._win32 --icon "%OUT%\wallwike.ico" --version-file "%OUT%\exe_info.txt" --distpath "%OUT%" --workpath "%OUT%\work" --specpath "%OUT%" "%HERE%\wallwike.py" > "%OUT%\build.log" 2>&1 || goto :fail
if not exist "%OUT%\Wallwike.exe" goto :fail

rem Keep the build folder tidy: just the app, its icon and the build log.
if exist "%OUT%\work" rmdir /s /q "%OUT%\work"
if exist "%OUT%\Wallwike.spec" del /f /q "%OUT%\Wallwike.spec"
if exist "%OUT%\exe_info.txt" del /f /q "%OUT%\exe_info.txt"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo.
echo Done!  Wallwike %VER% is ready in "%OUT%".

if defined WASRUNNING (
  echo Starting the new Wallwike...
  start "" "%OUT%\Wallwike.exe"
)
echo This window will close in 3 seconds...
>nul ping -n 4 127.0.0.1
exit /b 0

:fail
echo.
echo Build failed.
if defined OUT if exist "%OUT%\build.log" echo See "%OUT%\build.log" for details.
pause
exit /b 1
