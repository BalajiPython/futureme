import os
import multiprocessing

# Gunicorn config
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = max(2, multiprocessing.cpu_count())  # Use at least 2 workers
worker_class = 'sync'
timeout = 300  # Increased timeout for slow operations on Render
keepalive = 5
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
worker_connections = 1000
max_requests = 1000  # Restart workers periodically to prevent memory leaks
max_requests_jitter = 50

# WSGI application
wsgi_app = 'wsgi:application' 