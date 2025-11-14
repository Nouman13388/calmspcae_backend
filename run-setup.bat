@echo off
REM Setup script for Windows CMD
cd /d "d:\Github Desktop\calmspcae_backend"

echo Creating virtual environment...
python -m venv .venv

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo Running migrations...
python manage.py makemigrations
python manage.py migrate

echo Setting up user groups...
python manage.py setup_user_groups

echo.
echo ======================================
echo Setup complete!
echo ======================================
echo.
echo Next steps:
echo 1. Create .env file (copy from .env.example)
echo 2. Run: python manage.py runserver
echo.
pause
