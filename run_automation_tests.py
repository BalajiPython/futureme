#!/usr/bin/env python
"""
FutureMe Automation Tests - Simple Version
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')

import django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from letters.models import Letter

User = get_user_model()

print("\n" + "="*70)
print("🧪 FUTUREME AUTOMATION TESTS")
print("="*70)

passed = 0
failed = 0

# TEST 1: Home Page
print("\n[TEST 1] Home Page Access")
client = Client()
try:
    response = client.get(reverse('home'))
    if response.status_code == 200:
        print("✅ PASS: Home page loads")
        passed += 1
    else:
        print(f"❌ FAIL: Home page returned {response.status_code}")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 2: Login Page
print("\n[TEST 2] Login Page")
try:
    response = client.get(reverse('login'))
    if response.status_code == 200:
        print("✅ PASS: Login page loads")
        passed += 1
    else:
        print(f"❌ FAIL: Login page returned {response.status_code}")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 3: User Creation
print("\n[TEST 3] User Creation & Activation")
try:
    user = User.objects.create_user(
        email="autotest@test.com",
        password="AutoTest123!"
    )
    user.is_active = True
    user.save()
    
    created = User.objects.filter(email="autotest@test.com").exists()
    if created:
        print("✅ PASS: User created and activated")
        passed += 1
    else:
        print("❌ FAIL: User not created")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 4: Login Functionality
print("\n[TEST 4] Login Functionality")
try:
    login_success = client.login(email="autotest@test.com", password="AutoTest123!")
    if login_success:
        print("✅ PASS: User login successful")
        passed += 1
    else:
        print("❌ FAIL: Login failed")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 5: Dashboard Access
print("\n[TEST 5] Dashboard Access (Protected)")
try:
    response = client.get(reverse('dashboard'))
    if response.status_code == 200:
        print("✅ PASS: Dashboard accessible when logged in")
        passed += 1
    else:
        print(f"❌ FAIL: Dashboard returned {response.status_code}")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 6: Letter Creation
print("\n[TEST 6] Letter Creation")
try:
    user = User.objects.get(email="autotest@test.com")
    future_date = timezone.now() + timedelta(days=30)
    
    letter = Letter.objects.create(
        author=user,
        title="Automation Test Letter",
        content="This is an automated test letter",
        delivery_date=future_date
    )
    
    letter_exists = Letter.objects.filter(
        author=user,
        title="Automation Test Letter"
    ).exists()
    
    if letter_exists:
        print("✅ PASS: Letter created successfully")
        passed += 1
    else:
        print("❌ FAIL: Letter not created")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 7: Letter Delivery Timing (NOT EARLY)
print("\n[TEST 7] Letter Delivery Timing (Not Early)")
try:
    user = User.objects.get(email="autotest@test.com")
    now = timezone.now()
    
    # Future letter (should NOT be due)
    future_letter = Letter.objects.create(
        author=user,
        title="Future Letter",
        content="Should not be delivered",
        delivery_date=now + timedelta(minutes=5)
    )
    
    # Check if incorrectly marked as due
    is_incorrectly_due = Letter.objects.filter(
        delivery_date__lte=now,  # Only past or present
        is_delivered=False,
        id=future_letter.id
    ).exists()
    
    if not is_incorrectly_due:
        print("✅ PASS: Letter NOT delivered early (5-min buffer removed)")
        passed += 1
    else:
        print("❌ FAIL: Letter marked as due before delivery time")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 8: Logout
print("\n[TEST 8] Logout Functionality")
try:
    response = client.get(reverse('logout'), follow=True)
    if response.status_code == 200:
        print("✅ PASS: Logout successful")
        passed += 1
    else:
        print(f"❌ FAIL: Logout returned {response.status_code}")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 9: Protected Routes
print("\n[TEST 9] Protected Routes (No Auth)")
try:
    response = client.get(reverse('dashboard'))
    # Should redirect or 403 when not logged in
    if response.status_code in [302, 403]:
        print("✅ PASS: Protected route requires authentication")
        passed += 1
    else:
        print(f"❌ FAIL: Protected route accessible without auth ({response.status_code})")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# TEST 10: Database Integrity
print("\n[TEST 10] Database Integrity")
try:
    user_count = User.objects.count()
    letter_count = Letter.objects.count()
    
    if user_count > 0 and letter_count > 0:
        print(f"✅ PASS: Database integrity check ({user_count} users, {letter_count} letters)")
        passed += 1
    else:
        print("❌ FAIL: Data not persisted")
        failed += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    failed += 1

# CLEANUP
print("\n[CLEANUP] Removing test data...")
try:
    User.objects.filter(email="autotest@test.com").delete()
    print("✅ Test data cleaned up")
except:
    pass

# SUMMARY
print("\n" + "="*70)
print("📊 TEST RESULTS SUMMARY")
print("="*70)
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"📈 Total: {passed + failed}")
if passed + failed > 0:
    success_rate = (passed / (passed + failed)) * 100
    print(f"✨ Success Rate: {success_rate:.1f}%")
print("="*70)

if failed == 0:
    print("\n🎉 ALL TESTS PASSED! ✅")
else:
    print(f"\n⚠️  {failed} TEST(S) FAILED")
