@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where python >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Python was not found on PATH.
        echo Install Python 3 and try again.
        pause
        exit /b 1
    )
    python start_nisar_pulse.py
    exit /b %ERRORLEVEL%
)
py -3 start_nisar_pulse.py
exit /b %ERRORLEVEL%
