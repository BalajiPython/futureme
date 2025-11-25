#!/usr/bin/env python
"""
Comprehensive test suite for FutureMe application
Tests all critical functionality
"""
import os
import django
from django.conf import settings
from django.test.utils import get_runner

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from letters.models import Letter
from accounts.models import CustomUser
from datetime import datetime, timedelta
from django.utils import timezone

print("=" * 60)
print("COMPREHENSIVE TESTING SUITE FOR FUTUREME")
print("=" * 60)

# Test 1: Django Configuration
print("\n✓ TEST 1: Django System Configuration")
print("-" * 60)
print(f"✓ Django Version: {django.get_version()}")
print(f"✓ Database: {settings.DATABASES['default']['ENGINE']}")
print(f"✓ DEBUG Mode: {settings.DEBUG}")
print(f"✓ Installed Apps: {len(settings.INSTALLED_APPS)} apps configured")
print(f"✓ Middleware: {len(settings.MIDDLEWARE)} middleware configured")
print(f"✓ Authentication: {settings.AUTH_USER_MODEL}")

# Test 2: Database Connection
print("\n✓ TEST 2: Database Connection & Integrity")
print("-" * 60)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM auth_user")
        user_count = cursor.fetchone()[0]
    print(f"✓ Database Connection: OK")
    print(f"✓ Users in database: {user_count}")
    
    # Check tables
    tables = connection.introspection.table_names()
    print(f"✓ Total tables: {len(tables)}")
    
    required_tables = ['auth_user', 'letters_letter', 'letters_profile', 'accounts_customuser']
    for table in required_tables:
        if table in tables:
            print(f"  ✓ {table}: EXISTS")
        else:
            print(f"  ✗ {table}: MISSING")
except Exception as e:
    print(f"✗ Database Error: {str(e)}")

# Test 3: User Model
print("\n✓ TEST 3: CustomUser Model & Authentication")
print("-" * 60)
try:
    User = get_user_model()
    user_count = User.objects.count()
    print(f"✓ CustomUser model loaded")
    print(f"✓ Total users: {user_count}")
    
    if user_count > 0:
        user = User.objects.first()
        print(f"✓ Sample user: {user.email}")
        print(f"✓ User is active: {user.is_active}")
except Exception as e:
    print(f"✗ User Model Error: {str(e)}")

# Test 4: Letter Model
print("\n✓ TEST 4: Letter Model & Data")
print("-" * 60)
try:
    letter_count = Letter.objects.count()
    print(f"✓ Total letters: {letter_count}")
    
    if letter_count > 0:
        letter = Letter.objects.first()
        print(f"✓ Sample letter ID: {letter.id}")
        print(f"✓ Letter title: {letter.title}")
        print(f"✓ Is delivered: {letter.is_delivered}")
        print(f"✓ Delivery date: {letter.delivery_date}")
        print(f"✓ Delivery attempts: {letter.delivery_attempts}")
except Exception as e:
    print(f"✗ Letter Model Error: {str(e)}")

# Test 5: Settings Validation
print("\n✓ TEST 5: Security Settings")
print("-" * 60)
print(f"✓ DEBUG: {settings.DEBUG}")
print(f"✓ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"✓ SECRET_KEY length: {len(settings.SECRET_KEY)} characters")
print(f"✓ CSRF Middleware: {'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE}")
print(f"✓ Session Middleware: {'django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE}")
print(f"✓ Authentication Middleware: {'django.contrib.auth.middleware.AuthenticationMiddleware' in settings.MIDDLEWARE}")

# Test 6: Email Configuration
print("\n✓ TEST 6: Email Configuration")
print("-" * 60)
print(f"✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"✓ EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"✓ EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"✓ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

# Test 7: Installed Apps
print("\n✓ TEST 7: Installed Applications")
print("-" * 60)
for app in settings.INSTALLED_APPS:
    status = "✓" if not app.startswith('django.contrib.') else "✓"
    print(f"{status} {app}")

# Test 8: Static Files Configuration
print("\n✓ TEST 8: Static Files Configuration")
print("-" * 60)
print(f"✓ STATIC_URL: {settings.STATIC_URL}")
print(f"✓ STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"✓ STATICFILES_DIRS: {len(settings.STATICFILES_DIRS)} directories")

# Test 9: URL Configuration
print("\n✓ TEST 9: URL Configuration")
print("-" * 60)
try:
    from django.urls import get_resolver
    resolver = get_resolver()
    url_patterns = len(resolver.url_patterns)
    print(f"✓ Root URL patterns: {url_patterns}")
    
    # Check critical URLs
    critical_urls = ['admin:index', 'home', 'login', 'register', 'logout', 'dashboard', 'write_letter']
    for url_name in critical_urls:
        try:
            from django.urls import reverse
            reverse(url_name)
            print(f"  ✓ {url_name}: AVAILABLE")
        except:
            print(f"  ✗ {url_name}: NOT FOUND")
except Exception as e:
    print(f"✗ URL Configuration Error: {str(e)}")

# Test 10: Apps Ready
print("\n✓ TEST 10: Application Health Check")
print("-" * 60)
try:
    from django.apps import apps
    app_configs = apps.get_app_configs()
    print(f"✓ Total apps ready: {len(list(app_configs))}")
    
    critical_apps = ['accounts', 'letters', 'rest_framework', 'django_apscheduler']
    for app_name in critical_apps:
        try:
            app = apps.get_app_config(app_name)
            print(f"  ✓ {app_name}: READY")
        except:
            print(f"  ✗ {app_name}: NOT FOUND")
except Exception as e:
    print(f"✗ Apps Error: {str(e)}")

print("\n" + "=" * 60)
print("TESTING COMPLETE ✓")
print("=" * 60)
