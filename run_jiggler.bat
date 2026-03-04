@echo off
TITLE Mouse Jiggler
echo Starting Jiggler...
echo Press Ctrl+C to stop.
python windows_jiggler.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Python might not be installed or not in PATH.
    echo Please ensure Python is installed.
)
pause
