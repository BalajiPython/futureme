import os
import multiprocessing

# Gunicorn config
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = max(2, multiprocessing.cpu_count())
worker_class = 'sync'
timeout = 60  # Fast timeout since registration should be quick now
keepalive = 5
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
worker_connections = 1000
max_requests = 1000

# WSGI application
wsgi_app = 'wsgi:application' 