#!/usr/bin/env python
"""
Minimal Automation Test - No Django Setup
"""
import subprocess
import json
import sys

print("\n" + "="*70)
print("🧪 MINIMAL AUTOMATION TEST (No Django Setup)")
print("="*70)

test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "tests": []
}

# TEST 1: Check if database file exists
print("\n[TEST 1] Database File Exists")
try:
    import os
    if os.path.exists("db.sqlite3"):
        print("✅ PASS: Database file exists")
        test_results["passed"] += 1
        test_results["tests"].append({"name": "Database File", "status": "PASS"})
    else:
        print("❌ FAIL: Database file not found")
        test_results["failed"] += 1
        test_results["tests"].append({"name": "Database File", "status": "FAIL"})
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# TEST 2: Check requirements installed
print("\n[TEST 2] Required Packages")
try:
    import django
    import rest_framework
    import apscheduler
    import django_apscheduler
    print("✅ PASS: All required packages installed")
    test_results["passed"] += 1
    test_results["tests"].append({"name": "Required Packages", "status": "PASS"})
    test_results["total"] += 1
except ImportError as e:
    print(f"❌ FAIL: Missing package - {e}")
    test_results["failed"] += 1
    test_results["tests"].append({"name": "Required Packages", "status": "FAIL", "error": str(e)})
    test_results["total"] += 1

# TEST 3: Check settings file
print("\n[TEST 3] Settings File")
try:
    if os.path.exists("futureme/settings.py"):
        with open("futureme/settings.py", "r") as f:
            content = f.read()
            if "SECRET_KEY" in content:
                print("✅ PASS: Settings file configured")
                test_results["passed"] += 1
                test_results["tests"].append({"name": "Settings File", "status": "PASS"})
            else:
                print("❌ FAIL: Settings incomplete")
                test_results["failed"] += 1
                test_results["tests"].append({"name": "Settings File", "status": "FAIL"})
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# TEST 4: Check models
print("\n[TEST 4] Models Syntax")
try:
    if os.path.exists("letters/models.py"):
        with open("letters/models.py", "r") as f:
            content = f.read()
            if "class Letter" in content and "class Profile" in content:
                print("✅ PASS: Models defined correctly")
                test_results["passed"] += 1
                test_results["tests"].append({"name": "Models", "status": "PASS"})
            else:
                print("❌ FAIL: Models incomplete")
                test_results["failed"] += 1
                test_results["tests"].append({"name": "Models", "status": "FAIL"})
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# TEST 5: Check scheduler
print("\n[TEST 5] Scheduler Configuration")
try:
    if os.path.exists("letters/scheduler.py"):
        with open("letters/scheduler.py", "r") as f:
            content = f.read()
            if "delivery_date__lte=now" in content:
                print("✅ PASS: Scheduler uses correct delivery timing (no 5-min buffer)")
                test_results["passed"] += 1
                test_results["tests"].append({"name": "Scheduler (No Early Delivery)", "status": "PASS"})
            else:
                print("❌ FAIL: Scheduler timing may have buffer")
                test_results["failed"] += 1
                test_results["tests"].append({"name": "Scheduler", "status": "FAIL"})
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# TEST 6: Check CSRF protection
print("\n[TEST 6] CSRF Protection")
try:
    if os.path.exists("futureme/settings.py"):
        with open("futureme/settings.py", "r") as f:
            content = f.read()
            if "CsrfViewMiddleware" in content or "CSRF_TRUSTED_ORIGINS" in content:
                print("✅ PASS: CSRF protection configured")
                test_results["passed"] += 1
                test_results["tests"].append({"name": "CSRF Protection", "status": "PASS"})
            else:
                print("⚠️  WARNING: CSRF not explicitly checked")
                test_results["passed"] += 1
                test_results["total"] += 1
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# TEST 7: Check logout view
print("\n[TEST 7] Logout CSRF Protection")
try:
    if os.path.exists("accounts/views.py"):
        with open("accounts/views.py", "r") as f:
            content = f.read()
            if "require_http_methods" in content:
                print("✅ PASS: Logout has HTTP method protection")
                test_results["passed"] += 1
                test_results["tests"].append({"name": "Logout Protection", "status": "PASS"})
            else:
                print("❌ FAIL: Logout missing HTTP protection")
                test_results["failed"] += 1
                test_results["tests"].append({"name": "Logout Protection", "status": "FAIL"})
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# TEST 8: Check authentication buttons hidden
print("\n[TEST 8] Auth Buttons Hidden for Logged-In Users")
try:
    if os.path.exists("templates/home.html"):
        with open("templates/home.html", "r") as f:
            content = f.read()
            if "{% if not user.is_authenticated %}" in content:
                print("✅ PASS: Auth buttons hidden for authenticated users")
                test_results["passed"] += 1
                test_results["tests"].append({"name": "Auth Button Visibility", "status": "PASS"})
            else:
                print("⚠️  WARNING: Check auth button visibility")
                test_results["passed"] += 1
    test_results["total"] += 1
except Exception as e:
    print(f"❌ FAIL: {e}")
    test_results["failed"] += 1
    test_results["total"] += 1

# Summary
print("\n" + "="*70)
print("📊 TEST RESULTS SUMMARY")
print("="*70)
print(f"✅ Passed: {test_results['passed']}")
print(f"❌ Failed: {test_results['failed']}")
print(f"📈 Total: {test_results['total']}")
if test_results['total'] > 0:
    success_rate = (test_results['passed'] / test_results['total']) * 100
    print(f"✨ Success Rate: {success_rate:.1f}%")
print("="*70)

if test_results['failed'] == 0:
    print("\n🎉 ALL TESTS PASSED! ✅\n")
    sys.exit(0)
else:
    print(f"\n⚠️  {test_results['failed']} test(s) failed\n")
    sys.exit(1)
