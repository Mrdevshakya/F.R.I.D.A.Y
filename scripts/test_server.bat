@echo off
echo Starting FRIDAY Test Server...
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing required packages...
pip install Flask Flask-CORS
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

:: Start the test server
echo.
echo ==============================================
echo FRIDAY TEST SERVER is starting...
echo This server does NOT require the full FRIDAY backend
echo Access the web interface at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ==============================================
echo.

python server/test_server.py

:: This will execute if the server stops
echo.
echo FRIDAY Test Server has stopped.
pause 