@echo off
REM One-click launcher for the Fraud Detection app
REM - Activates local venv
REM - Starts backend Flask server

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\activate.bat" (
  echo Virtual environment not found at venv\Scripts\activate.bat
  echo Please create it or adjust this script.
  pause
  exit /b 1
)

call venv\Scripts\activate.bat
cd backend
python app.py
pause


