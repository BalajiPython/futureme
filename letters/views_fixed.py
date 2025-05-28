from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
import json
import random
import logging
import bleach
from datetime import datetime
from .models import Letter, PendingRegistration
from accounts.models import User
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

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
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        
        try:
            pending_reg = PendingRegistration.objects.get(
                email=email,
                otp_code=otp
            )
            
            # Get stored credentials from session
            stored_email = request.session.get('register_email')
            stored_password = request.session.get('register_password')
            
            if not stored_email or not stored_password or stored_email != email:
                messages.error(request, 'Registration session expired. Please register again.')
                return render(request, 'verify_otp.html')
            
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
            messages.success(request, 'Account verified successfully! Welcome to FutureMe.')
            return redirect('dashboard')
            
        except PendingRegistration.DoesNotExist:
            messages.error(request, 'Invalid or expired OTP')
            return render(request, 'verify_otp.html')
            
    return render(request, 'verify_otp.html')

@csrf_exempt
@require_http_methods(["POST"])
def verify_otp_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        otp_code = data.get('otp_code')

        if not email or not otp_code:
            return JsonResponse({'detail': 'Email and OTP code are required'}, status=400)

        session_email = request.session.get('register_email')
        session_password = request.session.get('register_password')
        session_otp = request.session.get('register_otp')

        if not (session_email and session_password and session_otp):
            return JsonResponse({'detail': 'No registration in progress. Please register first.'}, status=400)

        if email != session_email or otp_code != session_otp:
            return JsonResponse({'detail': 'Invalid OTP or email.'}, status=400)

        # Create user
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=None
            )
            user.password = session_password
            user.is_active = True
            user.save()

            # Clear session
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']

            login(request, user)
            return JsonResponse({'success': True, 'message': 'OTP verified and user created.'})
        except Exception as e:
            logger.error(f'User creation error: {str(e)}')
            return JsonResponse({'detail': 'Failed to create user account'}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'OTP verification error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500) 