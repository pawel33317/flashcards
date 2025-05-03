:: filepath: d:\fiszki\run_app.bat
@echo off
:: Navigate to the application directory
cd /d D:\fiszki

:: Start the application in a new terminal
start cmd /k "uvicorn app:app --reload"

:: Wait for the server to start
timeout /t 3 > nul

:: Open the application in the default browser
start http://localhost:8000