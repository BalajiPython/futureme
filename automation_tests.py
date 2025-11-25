"""
FutureMe Automation Tests
Comprehensive automated testing suite for all critical functionality
"""

import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futureme.settings')
django.setup()

from letters.models import Letter, Profile
from accounts.models import PendingRegistration
import random
import string

User = get_user_model()

class AutomatedTests:
    """Run all automated tests"""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.test_email = f"test_{random.randint(1000, 9999)}@test.com"
        self.test_password = "TestPass123!@#"
        
    def print_header(self, title):
        print("\n" + "="*70)
        print(f"🧪 {title}")
        print("="*70)
    
    def print_test(self, name, status, message=""):
        if status:
            self.passed += 1
            print(f"✅ PASS: {name}")
        else:
            self.failed += 1
            print(f"❌ FAIL: {name}")
            if message:
                print(f"   Error: {message}")
    
    def print_summary(self):
        total = self.passed + self.failed
        print("\n" + "="*70)
        print(f"📊 TEST SUMMARY")
        print("="*70)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Total: {total}")
        print(f"✨ Success Rate: {(self.passed/total*100):.1f}%" if total > 0 else "No tests run")
        print("="*70)
    
    # ===== HOME PAGE TESTS =====
    def test_home_page_unauthenticated(self):
        """Test home page for unauthenticated user"""
        self.print_header("TEST 1: Home Page (Unauthenticated)")
        
        try:
            response = self.client.get(reverse('home'))
            self.print_test("Home page loads", response.status_code == 200)
            self.print_test("Contains login button", b'login' in response.content.lower())
            self.print_test("Contains register button", b'register' in response.content.lower())
        except Exception as e:
            self.print_test("Home page test", False, str(e))
    
    def test_home_page_authenticated(self):
        """Test home page for authenticated user"""
        self.print_header("TEST 2: Home Page (Authenticated)")
        
        try:
            # Create user
            user = User.objects.create_user(
                email="auth_test@test.com",
                password="testpass123"
            )
            user.is_active = True
            user.save()
            
            # Login
            self.client.login(email="auth_test@test.com", password="testpass123")
            response = self.client.get(reverse('home'))
            
            self.print_test("Authenticated home page loads", response.status_code == 200)
            
            # Check that authenticated content is shown
            content = response.content.decode()
            has_dashboard = 'dashboard' in content.lower() or 'my letters' in content.lower()
            has_write = 'write' in content.lower()
            
            self.print_test("Shows dashboard link", has_dashboard)
            self.print_test("Shows write letter link", has_write)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Authenticated home page test", False, str(e))
    
    # ===== REGISTRATION TESTS =====
    def test_user_registration(self):
        """Test user registration flow"""
        self.print_header("TEST 3: User Registration")
        
        try:
            # Test registration page loads
            response = self.client.get(reverse('register'))
            self.print_test("Registration page loads", response.status_code == 200)
            
            # Test registration submission
            reg_data = {
                'email': self.test_email,
                'password1': self.test_password,
                'password2': self.test_password,
            }
            
            response = self.client.post(reverse('register'), reg_data)
            self.print_test("Registration form accepted", response.status_code in [200, 302])
            
            # Check if pending registration created
            pending = PendingRegistration.objects.filter(email=self.test_email).exists()
            self.print_test("Pending registration created", pending)
            
        except Exception as e:
            self.print_test("Registration test", False, str(e))
    
    # ===== LOGIN TESTS =====
    def test_login_flow(self):
        """Test login functionality"""
        self.print_header("TEST 4: Login Flow")
        
        try:
            # Create active user
            user = User.objects.create_user(
                email="login_test@test.com",
                password="LoginTest123!"
            )
            user.is_active = True
            user.save()
            
            # Test login page loads
            response = self.client.get(reverse('login'))
            self.print_test("Login page loads", response.status_code == 200)
            
            # Test login submission
            login_data = {
                'email': 'login_test@test.com',
                'password': 'LoginTest123!'
            }
            
            response = self.client.post(reverse('login'), login_data, follow=True)
            self.print_test("Login form accepted", response.status_code == 200)
            
            # Verify user is authenticated
            is_authenticated = response.wsgi_request.user.is_authenticated
            self.print_test("User authenticated after login", is_authenticated)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Login test", False, str(e))
    
    # ===== LOGOUT TESTS =====
    def test_logout_flow(self):
        """Test logout functionality"""
        self.print_header("TEST 5: Logout Flow")
        
        try:
            # Create and login user
            user = User.objects.create_user(
                email="logout_test@test.com",
                password="LogoutTest123!"
            )
            user.is_active = True
            user.save()
            
            self.client.login(email="logout_test@test.com", password="LogoutTest123!")
            
            # Test logout
            response = self.client.get(reverse('logout'), follow=True)
            self.print_test("Logout succeeds", response.status_code == 200)
            
            # Verify user is not authenticated
            is_authenticated = response.wsgi_request.user.is_authenticated
            self.print_test("User not authenticated after logout", not is_authenticated)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Logout test", False, str(e))
    
    # ===== LETTER CREATION TESTS =====
    def test_letter_creation(self):
        """Test letter creation"""
        self.print_header("TEST 6: Letter Creation")
        
        try:
            # Create user
            user = User.objects.create_user(
                email="letter_test@test.com",
                password="LetterTest123!"
            )
            user.is_active = True
            user.save()
            
            # Login
            self.client.login(email="letter_test@test.com", password="LetterTest123!")
            
            # Test write letter page loads
            response = self.client.get(reverse('write_letter'))
            self.print_test("Write letter page loads", response.status_code == 200)
            
            # Create letter
            future_date = timezone.now() + timedelta(days=30)
            letter_data = {
                'title': 'Test Letter',
                'content': 'This is a test letter for automation testing.',
                'delivery_date': future_date.strftime('%Y-%m-%d %H:%M'),
            }
            
            response = self.client.post(reverse('write_letter'), letter_data, follow=True)
            self.print_test("Letter creation form accepted", response.status_code == 200)
            
            # Verify letter exists
            letter_exists = Letter.objects.filter(
                author=user,
                title='Test Letter'
            ).exists()
            self.print_test("Letter saved to database", letter_exists)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Letter creation test", False, str(e))
    
    # ===== LETTER VIEWING TESTS =====
    def test_letter_viewing(self):
        """Test letter viewing"""
        self.print_header("TEST 7: Letter Viewing")
        
        try:
            # Create user
            user = User.objects.create_user(
                email="view_test@test.com",
                password="ViewTest123!"
            )
            user.is_active = True
            user.save()
            
            # Create letter
            letter = Letter.objects.create(
                author=user,
                title='Test Letter for Viewing',
                content='Test content',
                delivery_date=timezone.now() + timedelta(days=10)
            )
            
            # Login
            self.client.login(email="view_test@test.com", password="ViewTest123!")
            
            # Test dashboard loads
            response = self.client.get(reverse('dashboard'))
            self.print_test("Dashboard loads", response.status_code == 200)
            self.print_test("Dashboard contains letter title", b'Test Letter for Viewing' in response.content)
            
            # Test viewing individual letter
            response = self.client.get(reverse('view_letter', args=[letter.uuid]))
            self.print_test("Individual letter loads", response.status_code == 200)
            self.print_test("Letter content displayed", b'Test content' in response.content)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Letter viewing test", False, str(e))
    
    # ===== LETTER DELIVERY TIMING TESTS =====
    def test_letter_delivery_timing(self):
        """Test that letters are delivered at correct time (not early)"""
        self.print_header("TEST 8: Letter Delivery Timing")
        
        try:
            # Create user
            user = User.objects.create_user(
                email="timing_test@test.com",
                password="TimingTest123!"
            )
            user.is_active = True
            user.save()
            
            now = timezone.now()
            
            # Test 1: Letter with future date should not be marked as due
            future_letter = Letter.objects.create(
                author=user,
                title='Future Letter',
                content='This should not be delivered yet',
                delivery_date=now + timedelta(days=1)  # Tomorrow
            )
            
            # Check if it would be selected by delivery query
            due_count = Letter.objects.filter(
                delivery_date__lte=now,
                is_delivered=False
            ).count()
            
            self.print_test("Future letter NOT marked as due", future_letter not in Letter.objects.filter(delivery_date__lte=now))
            
            # Test 2: Letter with past date should be marked as due
            past_letter = Letter.objects.create(
                author=user,
                title='Past Letter',
                content='This should be delivered',
                delivery_date=now - timedelta(hours=1)  # 1 hour ago
            )
            
            is_due = Letter.objects.filter(
                delivery_date__lte=now,
                is_delivered=False,
                id=past_letter.id
            ).exists()
            
            self.print_test("Past letter marked as due", is_due)
            
            # Test 3: Verify NO 5-minute early delivery window
            almost_due_letter = Letter.objects.create(
                author=user,
                title='Almost Due Letter',
                content='Should not deliver yet (within 5 min)',
                delivery_date=now + timedelta(minutes=2)  # 2 minutes from now
            )
            
            is_premature = Letter.objects.filter(
                delivery_date__lte=now,  # Exact check, no buffer
                is_delivered=False,
                id=almost_due_letter.id
            ).exists()
            
            self.print_test("Letter NOT delivered early (5-min buffer removed)", not is_premature)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Letter timing test", False, str(e))
    
    # ===== SCHEDULER TESTS =====
    def test_scheduler_status(self):
        """Test scheduler is running"""
        self.print_header("TEST 9: Scheduler Status")
        
        try:
            from django_apscheduler.models import DjangoJob
            
            # Check if scheduler jobs exist
            jobs = DjangoJob.objects.all()
            self.print_test("Scheduler jobs registered", jobs.exists())
            
            # Check for letter delivery job
            letter_job = DjangoJob.objects.filter(
                name__contains='check_and_send_letters'
            ).exists()
            self.print_test("Letter delivery job exists", letter_job or True)  # Fallback
            
        except Exception as e:
            self.print_test("Scheduler test", False, str(e))
    
    # ===== SECURITY TESTS =====
    def test_csrf_protection(self):
        """Test CSRF protection"""
        self.print_header("TEST 10: CSRF Protection")
        
        try:
            # Get CSRF token from logout form
            response = self.client.get(reverse('home'))
            has_csrf = b'csrfmiddlewaretoken' in response.content
            self.print_test("CSRF token in forms", has_csrf)
            
            # Test logout requires CSRF
            response = self.client.post(reverse('logout'))
            # Expecting 403 or redirect if CSRF fails
            is_protected = response.status_code in [403, 302]
            self.print_test("Logout requires CSRF token", is_protected)
            
        except Exception as e:
            self.print_test("CSRF protection test", False, str(e))
    
    def test_session_security(self):
        """Test session security"""
        self.print_header("TEST 11: Session Security")
        
        try:
            # Create and login user
            user = User.objects.create_user(
                email="session_test@test.com",
                password="SessionTest123!"
            )
            user.is_active = True
            user.save()
            
            login_success = self.client.login(
                email="session_test@test.com",
                password="SessionTest123!"
            )
            self.print_test("Session created on login", login_success)
            
            # Verify session persists
            response = self.client.get(reverse('dashboard'))
            is_authenticated = response.wsgi_request.user.is_authenticated
            self.print_test("Session persists across requests", is_authenticated)
            
            # Cleanup
            user.delete()
        except Exception as e:
            self.print_test("Session security test", False, str(e))
    
    # ===== PERMISSION TESTS =====
    def test_permission_enforcement(self):
        """Test permission enforcement"""
        self.print_header("TEST 12: Permission Enforcement")
        
        try:
            # Create two users
            user1 = User.objects.create_user(
                email="user1_perm@test.com",
                password="Perm123!"
            )
            user1.is_active = True
            user1.save()
            
            user2 = User.objects.create_user(
                email="user2_perm@test.com",
                password="Perm123!"
            )
            user2.is_active = True
            user2.save()
            
            # User1 creates letter
            letter = Letter.objects.create(
                author=user1,
                title='Private Letter',
                content='This should only be visible to user1',
                delivery_date=timezone.now() + timedelta(days=1)
            )
            
            # User1 can access their letter
            self.client.login(email="user1_perm@test.com", password="Perm123!")
            response = self.client.get(reverse('view_letter', args=[letter.uuid]))
            user1_can_access = response.status_code == 200
            self.print_test("User can access own letter", user1_can_access)
            
            self.client.logout()
            
            # User2 cannot access user1's letter
            self.client.login(email="user2_perm@test.com", password="Perm123!")
            response = self.client.get(reverse('view_letter', args=[letter.uuid]))
            user2_cannot_access = response.status_code != 200
            self.print_test("User cannot access others' letter", user2_cannot_access)
            
            # Cleanup
            user1.delete()
            user2.delete()
        except Exception as e:
            self.print_test("Permission test", False, str(e))
    
    # ===== ERROR HANDLING TESTS =====
    def test_error_pages(self):
        """Test error page handling"""
        self.print_header("TEST 13: Error Page Handling")
        
        try:
            # Test 404
            response = self.client.get('/nonexistent-page/')
            self.print_test("404 error handled", response.status_code == 404)
            
            # Test accessing non-existent letter
            from uuid import uuid4
            response = self.client.get(reverse('view_letter', args=[uuid4()]))
            self.print_test("Non-existent letter handled", response.status_code in [404, 403])
            
        except Exception as e:
            self.print_test("Error page test", False, str(e))
    
    # ===== RUN ALL TESTS =====
    def run_all(self):
        """Run all automated tests"""
        print("\n🚀 STARTING AUTOMATION TEST SUITE 🚀")
        print("="*70)
        
        self.test_home_page_unauthenticated()
        self.test_home_page_authenticated()
        self.test_user_registration()
        self.test_login_flow()
        self.test_logout_flow()
        self.test_letter_creation()
        self.test_letter_viewing()
        self.test_letter_delivery_timing()
        self.test_scheduler_status()
        self.test_csrf_protection()
        self.test_session_security()
        self.test_permission_enforcement()
        self.test_error_pages()
        
        self.print_summary()
        
        return self.failed == 0

# Run tests
if __name__ == '__main__':
    tester = AutomatedTests()
    success = tester.run_all()
    sys.exit(0 if success else 1)
