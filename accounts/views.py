from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from django.contrib.auth import get_user_model
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from django.utils import timezone
from .models import PendingRegistration
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.core.cache import cache
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required

logger = logging.getLogger(__name__)
User = get_user_model()

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })

# Add this to your urlpatterns in accounts/urls.py
obtain_auth_token = CustomAuthToken.as_view()

def generate_otp():
    return ''.join(random.choices('0123456789', k=6))

@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')
        
        if not email or not password1 or not password2:
            return JsonResponse({'detail': 'Email and password are required'}, status=400)
            
        if password1 != password2:
            return JsonResponse({'detail': 'Passwords do not match'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'detail': 'Email already registered'}, status=400)
        
        # Generate OTP
        otp = generate_otp()
        
        # Store registration data in session
        request.session['register_email'] = email
        request.session['register_password'] = password1
        request.session['register_otp'] = otp
        
        # Create or update pending registration
        try:
            PendingRegistration.objects.update_or_create(
                email=email,
                defaults={'otp_code': otp, 'created_at': timezone.now()}
            )
            logger.info(f"Pending registration created for {email}")
        except Exception as e:
            logger.error(f"Failed to create pending registration: {str(e)}")
            return JsonResponse({
                'detail': 'Registration failed. Please try again.',
            }, status=500)
        
        # Send OTP email asynchronously with timeout
        email_sent = False
        try:
            # Use fail_silently=True to prevent timeout
            # Email sending should not block the response
            send_mail(
                subject='Verify your FutureMe account',
                message=f'Your OTP for FutureMe account verification is: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,  # Don't block on email failure
            )
            logger.info(f"OTP email sent to {email}")
            email_sent = True
        except Exception as e:
            logger.warning(f"Email sending exception (non-blocking): {str(e)}")
            # Don't fail registration if email fails - just log it
        
        # Always return success for registration (email is best-effort)
        return JsonResponse({
            'success': True,
            'message': 'Registration successful. Please check your email for the OTP.' if email_sent else 'Registration successful. Enter the OTP code.',
            'email': email,
            'otp_dev': otp if settings.DEBUG else None  # Show OTP in development only
        })
            
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        
        if not email or not otp:
            return JsonResponse({'detail': 'Email and OTP are required'}, status=400)
        
        try:
            pending_reg = PendingRegistration.objects.get(
                email=email,
                otp_code=otp
            )
            
            # Get stored credentials from session
            stored_email = request.session.get('register_email')
            stored_password = request.session.get('register_password')
            
            if not stored_email or not stored_password or stored_email != email:
                return JsonResponse({'detail': 'Registration session expired. Please register again.'}, status=400)
            
            # Create user with stored credentials
            user = User.objects.create_user(
                email=email,
                password=stored_password,
                is_active=True
            )
            
            # Clean up
            pending_reg.delete()
            # Clear session data
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']
            
            # Log in user
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Account verified successfully',
                'user': {
                    'email': user.email,
                    'is_superuser': user.is_superuser
                }
            })
            
        except PendingRegistration.DoesNotExist:
            return JsonResponse({'detail': 'Invalid or expired OTP'}, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'OTP verification error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def login_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JsonResponse({'detail': 'Email and password are required'}, status=400)
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Check password
            if not user.check_password(password):
                return JsonResponse({'detail': 'Invalid email or password'}, status=401)
            
            if not user.is_active:
                return JsonResponse({'detail': 'Account not activated. Please verify OTP.'}, status=403)
            
            # Log in user
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'email': user.email,
                    'is_superuser': user.is_superuser
                }
            })
            
        except User.DoesNotExist:
            return JsonResponse({'detail': 'Invalid email or password'}, status=401)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@require_http_methods(["POST"])
def resend_otp_view(request):
    email = request.session.get('pending_email')
    if not email:
        return JsonResponse({'success': False, 'error': 'No pending registration found'})
    
    try:
        # Check rate limit
        cache_key = f'otp_resend_{email}'
        last_resend = cache.get(cache_key)
        
        if last_resend:
            time_since_last_resend = timezone.now() - last_resend
            if time_since_last_resend < timedelta(minutes=1):
                remaining_seconds = 60 - time_since_last_resend.seconds
                return JsonResponse({
                    'success': False,
                    'error': f'Please wait {remaining_seconds} seconds before requesting a new OTP.',
                    'retry_after': remaining_seconds
                }, status=429)
        
        # Get existing pending registration
        try:
            pending_reg = PendingRegistration.objects.get(email=email)
        except PendingRegistration.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'No pending registration found for this email.'
            }, status=404)
        
        # Generate new OTP
        new_otp = generate_otp()
        pending_reg.otp_code = new_otp
        pending_reg.created_at = timezone.now()
        pending_reg.save()
        
        # Update rate limit
        cache.set(cache_key, timezone.now(), timeout=60)
        
        # Send new OTP email
        if send_verification_email(email, new_otp):
            return JsonResponse({
                'success': True,
                'message': 'New verification code sent successfully.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to send verification email. Please try again.'
            }, status=500)
            
    except Exception as e:
        logger.error(f'Resend OTP error: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=500)

def send_verification_email(email, verification_code):
    subject = 'Verify your FutureMe account'
    message = f'Your verification code for FutureMe account is: {verification_code}'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]
    
    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return False

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if not email or not password1 or not password2:
            messages.error(request, 'All fields are required.')
            return redirect('register')
            
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        
        # Store registration data in session
        request.session['register_email'] = email
        request.session['register_password'] = password1
        request.session['register_otp'] = otp
        
        # Create or update pending registration
        PendingRegistration.objects.update_or_create(
            email=email,
            defaults={'otp_code': otp, 'created_at': timezone.now()}
        )
        
        # Send OTP email
        try:
            send_mail(
                subject='Verify your FutureMe account',
                message=f'Your OTP for FutureMe account verification is: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Registration successful! Please check your email for OTP verification.')
            return redirect('verify_otp_view')
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            # Clean up the pending registration if email fails
            PendingRegistration.objects.filter(email=email).delete()
            # Clear session data
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']
            messages.error(request, 'Failed to send verification email. Please try again.')
            return redirect('register')
            
    return render(request, 'register.html')

def verify_otp_view(request):
    if request.method == 'POST':
        # Always get email from session
        email = request.session.get('register_email')
        otp = request.POST.get('otp')
        
        if not email or not otp:
            messages.error(request, 'All fields are required.')
            return render(request, 'verify_otp.html')
        
        try:
            pending_reg = PendingRegistration.objects.get(
                email=email,
                otp_code=otp
            )
            
            stored_password = request.session.get('register_password')
            if not stored_password:
                messages.error(request, 'Registration session expired. Please register again.')
                return render(request, 'verify_otp.html')
            
            user = User.objects.create_user(
                email=email,
                password=stored_password,
                is_active=True
            )
            pending_reg.delete()
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']
            login(request, user)
            messages.success(request, 'Account verified successfully! Welcome to FutureMe.')
            return redirect('dashboard')
        except PendingRegistration.DoesNotExist:
            messages.error(request, 'Invalid or expired OTP')
            return render(request, 'verify_otp.html')
    return render(request, 'verify_otp.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Please provide both email and password')
            return render(request, 'login.html')
        
        try:
            # Find user by email
            user = User.objects.get(email=email)
            
            # Check password
            if user.check_password(password):
                if not user.is_active:
                    messages.error(request, 'Your account is not activated. Please check your email for activation link.')
                    return render(request, 'login.html')
                
                # Log in user
                login(request, user)
                messages.success(request, 'Successfully logged in!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'login.html')
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'login.html')
            
    return render(request, 'login.html')

@require_http_methods(["GET", "POST"])
def logout_view(request):
    """Logout the user and redirect to home"""
    if request.user.is_authenticated:
        logger.info(f"User logged out: {request.user.email}")
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home')

@staff_member_required
def delete_user_view(request):
    return render(request, 'delete_user.html')

@csrf_exempt
@staff_member_required
@require_http_methods(["POST"])
def delete_user_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'detail': 'Email is required'}, status=400)
        
        try:
            user = User.objects.get(email=email)
            user.delete()
            logger.info(f"User deleted successfully by admin {request.user.email}: {email}")
            return JsonResponse({
                'success': True,
                'message': f'User with email {email} has been deleted successfully'
            })
        except User.DoesNotExist:
            logger.error(f"User not found with email: {email}")
            return JsonResponse({
                'detail': 'User not found with this email'
            }, status=404)
            
    except Exception as e:
        logger.error(f'Delete user error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@staff_member_required
def list_superusers_view(request):
    superusers = User.objects.filter(is_superuser=True)
    return render(request, 'list_superusers.html', {
        'superusers': superusers
    })
