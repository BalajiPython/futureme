web: gunicorn futureme.wsgi:application --bind 0.0.0.0:$PORT
worker: python manage.py start_scheduler 