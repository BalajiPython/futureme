web: cd futureme && gunicorn wsgi:application --bind 0.0.0.0:$PORT
worker: cd futureme && python manage.py start_scheduler 