@echo off
REM Development server startup script
cd /d "%~dp0"
set DEBUG=True
echo Starting FutureMe Development Server...
echo.
echo Access the application at: http://127.0.0.1:8000
echo.
python manage.py runserver
