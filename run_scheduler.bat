@echo off
echo Starting FutureSelf Letter Scheduler...
:loop
python manage.py start_scheduler
echo Scheduler stopped, restarting in 5 seconds...
timeout /t 5
goto loop 