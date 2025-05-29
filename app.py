import os
import sys

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')

from django.core.wsgi import get_wsgi_application

# Initialize Django application
app = get_wsgi_application() 