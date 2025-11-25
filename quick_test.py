import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')
django.setup()

print("="*60)
print("FUTUREME APPLICATION TEST REPORT")
print("="*60)

# Test 1: Django Check
print("\n[TEST 1] Django System Check")
print("-"*60)
from django.core.management import execute_from_command_line
try:
    execute_from_command_line(['manage.py', 'check', '--quiet'])
    print("✓ Django system check: PASSED")
except:
    print("✗ Django system check: FAILED")

# Test 2: Database
print("\n[TEST 2] Database Connection")
print("-"*60)
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection: OK")
except Exception as e:
    print(f"✗ Database connection: FAILED - {e}")

# Test 3: Models
print("\n[TEST 3] Django Models")
print("-"*60)
try:
    from accounts.models import CustomUser
    from letters.models import Letter, Profile
    print(f"✓ CustomUser model: OK")
    print(f"✓ Letter model: OK")
    print(f"✓ Profile model: OK")
except Exception as e:
    print(f"✗ Models: FAILED - {e}")

# Test 4: Users
print("\n[TEST 4] User Data")
print("-"*60)
try:
    from accounts.models import CustomUser
    user_count = CustomUser.objects.count()
    print(f"✓ Total users: {user_count}")
except Exception as e:
    print(f"✗ User check: FAILED - {e}")

# Test 5: Letters
print("\n[TEST 5] Letter Data")
print("-"*60)
try:
    from letters.models import Letter
    letter_count = Letter.objects.count()
    due_count = Letter.objects.filter(delivery_date__lte=django.utils.timezone.now(), is_delivered=False).count()
    print(f"✓ Total letters: {letter_count}")
    print(f"✓ Due letters: {due_count}")
except Exception as e:
    print(f"✗ Letter check: FAILED - {e}")

# Test 6: Settings
print("\n[TEST 6] Settings Validation")
print("-"*60)
from django.conf import settings
print(f"✓ SECRET_KEY: {'SET' if settings.SECRET_KEY else 'NOT SET'}")
print(f"✓ DEBUG: {settings.DEBUG}")
print(f"✓ ALLOWED_HOSTS: {len(settings.ALLOWED_HOSTS)} hosts")
print(f"✓ DATABASE: {settings.DATABASES['default']['NAME']}")

# Test 7: Apps
print("\n[TEST 7] Installed Apps")
print("-"*60)
from django.apps import apps
app_names = [app.name for app in apps.get_app_configs()]
critical_apps = ['accounts', 'letters', 'rest_framework']
for app in critical_apps:
    status = "✓" if app in app_names else "✗"
    print(f"{status} {app}")

# Test 8: URLs
print("\n[TEST 8] URL Routes")
print("-"*60)
from django.urls import reverse
urls_to_test = ['home', 'login', 'register', 'logout', 'dashboard']
for url_name in urls_to_test:
    try:
        reverse(url_name)
        print(f"✓ {url_name}")
    except:
        print(f"✗ {url_name}: NOT FOUND")

print("\n" + "="*60)
print("TESTING COMPLETE ✓")
print("="*60)
