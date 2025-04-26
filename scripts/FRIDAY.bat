@echo off
echo.
echo =========================================
echo           FRIDAY AI ASSISTANT           
echo =========================================
echo.

:: Parse command-line arguments
set GUI_MODE=0
set NO_VOICE=0
set CLEAN_LOGS=0
set DEBUG_MODE=0

:parse_args
if "%~1"=="" goto :main
if /i "%~1"=="--gui" set GUI_MODE=1
if /i "%~1"=="--no-voice" set NO_VOICE=1
if /i "%~1"=="--clean" set CLEAN_LOGS=1
if /i "%~1"=="--debug" set DEBUG_MODE=1
shift
goto :parse_args

:main
:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the PATH. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

:: Install dependencies if venv not found
if not exist "venv\" (
    echo Installing virtual environment and dependencies...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Please try installing them manually.
        echo Run: pip install -r requirements.txt
        pause
        exit /b 1
    )
) else (
    :: Activate the virtual environment
    call venv\Scripts\activate.bat
)

:: Prepare command arguments
set "CMD_ARGS="
if %NO_VOICE%==1 set "CMD_ARGS=%CMD_ARGS% --no-voice"
if %CLEAN_LOGS%==1 set "CMD_ARGS=%CMD_ARGS% --clean"
if %DEBUG_MODE%==1 set "CMD_ARGS=%CMD_ARGS% --debug"

:: Start FRIDAY in the appropriate mode
if %GUI_MODE%==1 (
    echo Starting FRIDAY in GUI mode...
    start python backend/chat_ui.py %CMD_ARGS%
) else (
    echo Starting FRIDAY in console mode...
    python backend/main.py %CMD_ARGS%
)

:: Deactivate virtual environment when done
deactivate 