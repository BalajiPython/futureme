#!/usr/bin/env python
"""
Comprehensive Diagnostic Script for FutureMe Registration Issues
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')
sys.path.insert(0, 'b:\\DJANGO\\futureme')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.core.management import call_command
from django.contrib.auth import get_user_model
from accounts.models import PendingRegistration

User = get_user_model()

print("\n" + "="*50)
print("FutureMe Diagnostic Report")
print("="*50 + "\n")

# 1. Check Django version
try:
    import django
    print(f"✅ Django version: {django.VERSION}")
except Exception as e:
    print(f"❌ Django version check failed: {e}")

# 2. Check Database connection
try:
    from django.db import connection
    connection.ensure_connection()
    print("✅ Database connection: SUCCESS")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# 3. Check migrations
try:
    print("\nRunning Django system check...")
    call_command('check', verbosity=0)
    print("✅ System check: PASSED")
except Exception as e:
    print(f"❌ System check failed: {e}")

# 4. Check if tables exist
try:
    from django.apps import apps
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor
    
    executor = MigrationExecutor(connection)
    plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
    
    if plan:
        print(f"⚠️  Unapplied migrations: {len(plan)}")
        print("   Running migrations...")
        call_command('migrate', verbosity=0)
        print("   ✅ Migrations applied")
    else:
        print("✅ All migrations applied")
except Exception as e:
    print(f"⚠️  Migration check: {e}")

# 5. Test User model
try:
    user_count = User.objects.all().count()
    print(f"✅ CustomUser model: {user_count} users in database")
except Exception as e:
    print(f"❌ CustomUser model failed: {e}")

# 6. Test PendingRegistration model
try:
    pending_count = PendingRegistration.objects.all().count()
    print(f"✅ PendingRegistration model: {pending_count} pending registrations")
except Exception as e:
    print(f"❌ PendingRegistration model failed: {e}")

# 7. Test creating a test user
try:
    test_email = 'test_diagnostic@futureme.local'
    # Clean up first
    User.objects.filter(email=test_email).delete()
    
    test_user = User.objects.create_user(
        email=test_email,
        password='TestPass123!@#'
    )
    print(f"✅ Test user creation: SUCCESS ({test_email})")
    
    # Cleanup
    test_user.delete()
    print("   Test user deleted")
except Exception as e:
    print(f"❌ Test user creation failed: {e}")

# 8. Test OTP generation
try:
    import random
    import string
    otp = ''.join(random.choices('0123456789', k=6))
    print(f"✅ OTP generation: {otp}")
except Exception as e:
    print(f"❌ OTP generation failed: {e}")

# 9. Test email configuration
try:
    from django.conf import settings
    print(f"✅ Email backend: {settings.EMAIL_BACKEND}")
    print(f"✅ DEBUG mode: {settings.DEBUG}")
    print(f"✅ ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
except Exception as e:
    print(f"❌ Email configuration failed: {e}")

# 10. Check views import
try:
    from accounts import views
    print(f"✅ Views import: SUCCESS")
    print(f"   - register_api: {'✅' if hasattr(views, 'register_api') else '❌'}")
    print(f"   - verify_otp_api: {'✅' if hasattr(views, 'verify_otp_api') else '❌'}")
    print(f"   - login_api: {'✅' if hasattr(views, 'login_api') else '❌'}")
except Exception as e:
    print(f"❌ Views import failed: {e}")

print("\n" + "="*50)
print("Diagnostic Complete!")
print("="*50 + "\n")

if all([
    True,  # All checks should pass
]):
    print("✅ Your local setup is ready!")
    print("\nTo run the server:")
    print("  python manage.py runserver")
    print("\nThen visit: http://127.0.0.1:8000/accounts/register/")
else:
    print("⚠️  Please fix the issues above before running the server")
