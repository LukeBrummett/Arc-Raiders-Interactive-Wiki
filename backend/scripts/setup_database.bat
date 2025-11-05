@echo off
REM PostgreSQL Database Setup Script for Arc Raiders Wiki
REM This script creates the database and user

echo ============================================
echo Arc Raiders Wiki - Database Setup
echo ============================================
echo.

REM Set PostgreSQL bin directory
set PGBIN=C:\Program Files\PostgreSQL\15\bin

echo Step 1: Creating database and user...
echo.
echo You'll be prompted for the postgres superuser password.
echo (This was set during PostgreSQL installation)
echo.

"%PGBIN%\psql.exe" -U postgres -c "CREATE DATABASE arcraiders_wiki;"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to create database. Checking if it already exists...
    "%PGBIN%\psql.exe" -U postgres -l | findstr arcraiders_wiki
    if %ERRORLEVEL% EQU 0 (
        echo Database 'arcraiders_wiki' already exists!
    ) else (
        echo.
        echo ERROR: Could not connect to PostgreSQL.
        echo.
        echo Possible solutions:
        echo 1. Reset postgres password using pgAdmin
        echo 2. Or we can create a .pgpass file to store credentials
        echo 3. Or use Windows authentication instead
        pause
        exit /b 1
    )
)

echo.
echo ============================================
echo Database setup complete!
echo ============================================
echo.
echo Next steps:
echo 1. Run: alembic upgrade head
echo 2. Run: python test_db.py
echo.
pause
