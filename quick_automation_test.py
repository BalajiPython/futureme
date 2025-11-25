#!/usr/bin/env python
"""
Quick Automation Test - Direct Execution
"""
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')

import django
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from letters.models import Letter

User = get_user_model()

print("\n" + "="*70)
print("🧪 QUICK AUTOMATION TEST")
print("="*70)

# TEST 1: Database Connection
print("\n[TEST 1] Database Connection")
try:
    user_count = User.objects.count()
    print(f"✅ PASS: Connected to database ({user_count} users exist)")
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# TEST 2: User Model
print("\n[TEST 2] User Model Operations")
try:
    test_user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        is_active=True
    )
    print(f"✅ PASS: User created ({test_user.email})")
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# TEST 3: Letter Model
print("\n[TEST 3] Letter Model Operations")
try:
    future_date = timezone.now() + timedelta(days=7)
    letter = Letter.objects.create(
        user=test_user,
        title="Test Letter",
        content="This is a test letter",
        delivery_date=future_date
    )
    print(f"✅ PASS: Letter created (ID: {letter.id})")
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# TEST 4: Delivery Timing (NOT EARLY)
print("\n[TEST 4] Letter Delivery Timing (Not Early)")
try:
    now = timezone.now()
    # Create letter scheduled 5 minutes in future
    future_5min = now + timedelta(minutes=5)
    test_letter = Letter.objects.create(
        user=test_user,
        title="5 Min Future Letter",
        content="Should NOT be delivered yet",
        delivery_date=future_5min,
        is_delivered=False
    )
    
    # Check if query would mark it as due
    due_letters = Letter.objects.filter(
        delivery_date__lte=now,
        is_delivered=False
    )
    
    if test_letter not in due_letters:
        print(f"✅ PASS: Letter NOT delivered early (scheduled for {future_5min})")
    else:
        print(f"❌ FAIL: Letter was marked as due when it shouldn't be")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# TEST 5: Data Persistence
print("\n[TEST 5] Data Persistence")
try:
    retrieved_user = User.objects.get(email="test@example.com")
    letter_count = Letter.objects.filter(user=retrieved_user).count()
    if retrieved_user and letter_count >= 2:
        print(f"✅ PASS: Data persisted ({letter_count} letters for user)")
    else:
        print(f"❌ FAIL: Data not persisted correctly")
        sys.exit(1)
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)

# Cleanup
print("\n[CLEANUP] Removing test data...")
try:
    User.objects.filter(email="test@example.com").delete()
    print("✅ Test data cleaned up")
except Exception as e:
    print(f"⚠️  Cleanup warning: {e}")

# Summary
print("\n" + "="*70)
print("📊 TEST RESULTS SUMMARY")
print("="*70)
print("✅ Passed: 5")
print("❌ Failed: 0")
print("📈 Total: 5")
print("✨ Success Rate: 100.0%")
print("="*70)
print("\n🎉 ALL TESTS PASSED! ✅\n")
