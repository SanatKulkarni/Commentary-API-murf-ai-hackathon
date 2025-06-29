@echo off
echo ===== Video Commentary Generator =====
echo This script will process a video file and generate a commentary with TTS audio.

REM Check for required file
if not exist "qr-tweet-marketer-demo-sanat.mp4" (
    echo Error: Video file 'qr-tweet-marketer-demo-sanat.mp4' not found!
    echo Please make sure the file is in the current directory.
    pause
    exit /b 1
)

echo.
echo Step 1: Starting Flask server...
start /B python video_summarization_backend.py
echo Waiting for Flask server to start...
timeout /t 5 /nobreak

echo.
echo Step 2: Generating commentary JSON...
python test_api.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to generate commentary JSON!
    pause
    exit /b 1
)

echo.
echo Step 3: Generating TTS audio files...
python audio_generator.py
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to generate audio files!
    pause
    exit /b 1
)

echo.
echo All steps completed successfully!
echo.
echo You can find:
echo - The JSON commentary in 'commentary_output.json'
echo - Audio files in the 'audio_output' directory
echo.
echo Audio files are named sequentially as 01_funny.mp3, 02_informative.mp3, etc.
echo.
echo Press any key to exit...

pause
