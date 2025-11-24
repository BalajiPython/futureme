from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods, require_GET
from django.core.mail import send_mail
from django.conf import settings
from .models import Letter, PendingRegistration
import json
import random
import logging
import bleach
from django.utils import timezone
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def home_view(request):
    return render(request, 'index.html')

@login_required(login_url='/login/')
def dashboard(request):
    letters = Letter.objects.filter(author=request.user).order_by('delivery_date')
    return render(request, 'dashboard.html', {'letters': letters})

from .models import PendingRegistration
from django.contrib.auth.hashers import make_password

@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'detail': 'Email and password are required'}, status=400)

        if User.objects.filter(email=email).exists() or PendingRegistration.objects.filter(email=email).exists():
            return JsonResponse({'detail': 'Email already registered or pending verification'}, status=400)

        # Generate 6-digit OTP
        otp_code = ''.join(random.choices('0123456789', k=6))

        # Save or update PendingRegistration with hashed password and OTP
        PendingRegistration.objects.update_or_create(
            email=email,
            defaults={
                'otp_code': otp_code
            }
        )

        # Send OTP email synchronously
        subject = 'Your OTP Code for FutureSelf'
        message = f'Your OTP code is: {otp_code}. It will expire in 10 minutes.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]
        send_mail(subject, message, from_email, recipient_list)

        return JsonResponse({'success': True, 'message': 'Registration successful. Please verify OTP sent to your email.'})

    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@require_GET
def verify_otp_view(request):
    # Render the OTP verification page
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

        try:
            pending = PendingRegistration.objects.get(email=email)
        except PendingRegistration.DoesNotExist:
            return JsonResponse({'detail': 'Pending registration not found. Please register again.'}, status=404)

        if pending.is_expired():
            pending.delete()
            return JsonResponse({'detail': 'OTP expired. Please register again.'}, status=400)

        if pending.otp_code != otp_code:
            return JsonResponse({'detail': 'Invalid OTP code'}, status=400)

        # OTP is valid, create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None
        )
        user.is_active = True
        user.save()

        # Delete pending registration after successful verification
        pending.delete()

        # Log in the user
        login(request, user)

        return JsonResponse({'success': True, 'message': 'OTP verified successfully'})

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

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if not user.is_active:
                return JsonResponse({'detail': 'Account not activated. Please verify your email.'}, status=403)
            login(request, user)
            return JsonResponse({'success': True})

        return JsonResponse({'detail': 'Invalid credentials'}, status=401)

    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'register.html')

@csrf_protect
def write_letter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        content = bleach.clean(
            data['content'],
            tags=['p', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'br', 'ul', 'ol', 'li'],
            strip=True
        )

        # Parse delivery_date string to datetime object
        try:
            delivery_dt = datetime.fromisoformat(data['delivery_date'].replace('Z', '+00:00'))
        except Exception:
            return JsonResponse({'detail': 'Invalid delivery date format'}, status=400)

        # Validate delivery datetime is at least 1 minute after now
        now = timezone.now()
        logger.info(f"Parsed delivery_date: {delivery_dt}, Current server time: {now}")
        if delivery_dt < now + timedelta(minutes=1):
            return JsonResponse({'detail': 'Delivery time must be at least 1 minute from now'}, status=400)

        letter = Letter.objects.create(
            author=request.user,
            title=data['title'],
            content=content,
            delivery_date=delivery_dt
        )

        # Send letter synchronously if delivery_date is now or past (optional)
        if delivery_dt <= now:
            subject = f"Letter from your past self: {letter.title}"
            message = letter.content
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [request.user.email]
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                logger.error(f'Error sending letter email: {str(e)}')
                return JsonResponse({'detail': 'Failed to send letter email'}, status=500)

        return JsonResponse({
            'id': letter.id,
            'message': 'Letter scheduled successfully'
        })
    return render(request, 'write.html')

@login_required
def api_letters(request):
    letters = Letter.objects.filter(author=request.user).values()
    return JsonResponse({'letters': list(letters)})

def logout_view(request):
    logout(request)
    return redirect('login')
