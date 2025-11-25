@echo off
cls
echo ========================================
echo FutureMe - Local Server Test
echo ========================================
echo.

cd /d b:\DJANGO\futureme

echo Checking Python...
"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" --version

echo.
echo Running Django checks...
"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py check

echo.
echo Applying migrations...
"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py migrate

echo.
echo ========================================
echo Starting development server...
echo ========================================
echo.
echo Access your app at: http://127.0.0.1:8000
echo.

"C:\Users\balaji\AppData\Local\Programs\Python\Python312\python.exe" manage.py runserver 0.0.0.0:8000

pause
