@echo off
echo ===== Installing Required Dependencies =====
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install required Python packages!
    echo Please make sure pip is installed and try again.
    pause
    exit /b 1
)

echo.

echo.
echo Setup complete. You can now run run_all.bat to generate commentary.
pause
