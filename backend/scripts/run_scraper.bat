@echo off
REM Wrapper script to run populate_database.py with proper venv activation

echo ============================================
echo Arc Raiders Wiki - Database Population
echo ============================================
echo.

cd /d "%~dp0"

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo Virtual environment activated
    echo.
    python populate_database.py %*
) else (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)
