from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from .models import Letter
from accounts.models import PendingRegistration
import json
import random
import logging
import bleach
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password
from django.db import transaction

logger = logging.getLogger(__name__)
User = get_user_model()  # Get the custom user model

def send_otp_email(email, otp):
    """Send OTP email to user"""
    logger.info(f"[OTP] Sending OTP email to {email}")
    logger.info(f"[OTP] Generated OTP: {otp}")
    
    subject = 'Your FutureMe Verification Code'
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #333;">Welcome to FutureMe!</h2>
            <p>Thank you for registering. Please use the following verification code to complete your registration:</p>
            <h1 style="color: #007bff; font-size: 48px; text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">{otp}</h1>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #666; font-size: 12px;">This is an automated message, please do not reply.</p>
        </body>
    </html>
    """
    plain_message = f'Your FutureMe verification code is: {otp}'
    
    try:
        logger.info(f"[OTP] Email settings - Host: {settings.EMAIL_HOST}, Port: {settings.EMAIL_PORT}")
        logger.info(f"[OTP] From email: {settings.EMAIL_HOST_USER}")
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"[OTP] Successfully sent OTP email to {email}")
        return True
    except Exception as e:
        logger.error(f"[OTP] Failed to send OTP email: {str(e)}")
        return False

def home_view(request):
    return render(request, 'index.html')

@login_required
def dashboard(request):
    """Display user's letters and their status"""
    try:
        # Get all letters for the current user, ordered by delivery date
        letters = Letter.objects.filter(author=request.user).order_by('-delivery_date')
        
        # Process each letter to determine its status
        for letter in letters:
            now = timezone.now()
            
            # Update status based on delivery date and is_delivered flag
            if letter.is_delivered:
                letter.status = 'Delivered'
                letter.status_class = 'success'
            elif letter.delivery_date <= now:
                letter.status = 'Overdue'
                letter.status_class = 'danger'
            else:
                time_diff = letter.delivery_date - now
                if time_diff.days > 0:
                    letter.status = f'In {time_diff.days} days'
                elif time_diff.seconds >= 3600:
                    hours = time_diff.seconds // 3600
                    letter.status = f'In {hours} hours'
                else:
                    minutes = time_diff.seconds // 60
                    letter.status = f'In {minutes} minutes'
                letter.status_class = 'info'
            
            # Add delivery time information
            if letter.is_delivered and letter.sent_at:
                letter.delivery_time = letter.sent_at.strftime('%Y-%m-%d %H:%M:%S UTC')
            else:
                letter.delivery_time = letter.delivery_date.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        context = {
            'letters': letters,
            'user': request.user
        }
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error in dashboard view: {str(e)}")
        messages.error(request, "An error occurred while loading your dashboard.")
        return redirect('home')

@csrf_exempt
@require_http_methods(["POST"])
def register_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password1 = data.get('password1')
        password2 = data.get('password2')

        # Validate email
        if not email:
            return JsonResponse({'detail': 'Email is required'}, status=400)

        # Validate passwords
        if not password1 or not password2:
            return JsonResponse({'detail': 'Both password fields are required'}, status=400)

        if password1 != password2:
            return JsonResponse({'detail': 'Passwords do not match'}, status=400)

        # Check if email is already registered
        if User.objects.filter(email=email).exists():
            return JsonResponse({'detail': 'Email already registered'}, status=400)
        
        # Check if there's a pending registration
        if PendingRegistration.objects.filter(email=email).exists():
            return JsonResponse({'detail': 'Email already has a pending registration'}, status=400)

        # Generate 6-digit OTP
        otp_code = ''.join(random.choices('0123456789', k=6))

        # Store registration data in session
        request.session['register_email'] = email
        request.session['register_password'] = password1
        request.session['register_otp'] = otp_code

        # Create pending registration
        PendingRegistration.objects.create(
            email=email,
            otp_code=otp_code
        )

        # Send OTP email
        try:
            send_mail(
                subject='Your FutureMe Verification Code',
                message=f'Your verification code is: {otp_code}. It will expire in 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            return JsonResponse({
                'success': True,
                'message': 'Registration successful. Please check your email for the verification code.',
                'email': email
            })
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            # Clean up the pending registration if email fails
            PendingRegistration.objects.filter(email=email).delete()
            # Clear session data
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']
            return JsonResponse({
                'detail': 'Failed to send verification email. Please try again.',
                'error': str(e)
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Registration error: {str(e)}')
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
            return JsonResponse({'success': True, 'message': 'Login successful'})
            
        except User.DoesNotExist:
            return JsonResponse({'detail': 'Invalid email or password'}, status=401)
        
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f'Login error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@csrf_protect
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
                email=email,
                password=session_password,
                is_active=True
            )

            # Clear session
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']

            # Log in user
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

@require_http_methods(["GET", "POST"])
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
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password')
                return render(request, 'login.html')
                
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'login.html')
            
    return render(request, 'login.html')

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
        
        # Check if there's an existing pending registration
        try:
            pending_reg = PendingRegistration.objects.get(email=email)
            pending_reg.otp_code = otp
            pending_reg.created_at = timezone.now()
            pending_reg.save()
        except PendingRegistration.DoesNotExist:
            pending_reg = PendingRegistration.objects.create(
                email=email,
                otp_code=otp
            )
        
        # Send OTP email
        if send_otp_email(email, otp):
            messages.success(request, 'Registration successful! Please check your email for OTP verification.')
            return redirect('verify_otp_view')
        else:
            messages.error(request, 'Failed to send verification email. Please try again.')
            # Clean up session data
            del request.session['register_email']
            del request.session['register_password']
            del request.session['register_otp']
            return redirect('register')
            
    return render(request, 'register.html')

@login_required
@require_http_methods(["GET", "POST"])
def write_letter(request):
    if request.method == "GET":
        return render(request, 'write.html')
        
    try:
        data = json.loads(request.body)
        title = data.get('title')
        content = data.get('content')
        delivery_date_str = data.get('delivery_date')
        timezone_offset = data.get('timezone_offset', 0)  # Get timezone offset in minutes
        
        logger.info(f"\n=== Letter Creation Debug ===")
        logger.info(f"Received letter data:")
        logger.info(f"Title: {title}")
        logger.info(f"Delivery Date (raw): {delivery_date_str}")
        logger.info(f"Timezone Offset: {timezone_offset} minutes")
        
        if not all([title, content, delivery_date_str]):
            logger.error("Missing required fields")
            return JsonResponse({'error': 'All fields are required'}, status=400)
        
        try:
            # Parse the ISO datetime string
            delivery_date = datetime.fromisoformat(delivery_date_str.replace('Z', '+00:00'))
            
            # Make sure it's timezone-aware
            if timezone.is_naive(delivery_date):
                delivery_date = timezone.make_aware(delivery_date)
            
            # Get current time in UTC
            now = timezone.now()
            
            logger.info(f"Time comparison:")
            logger.info(f"Current time (UTC): {now}")
            logger.info(f"Delivery time (UTC): {delivery_date}")
            logger.info(f"Time difference: {delivery_date - now}")
            
            if delivery_date <= now:
                logger.error("Delivery date is not in the future")
                return JsonResponse({'error': 'Delivery date must be in the future'}, status=400)
            
            # Sanitize content
            sanitized_content = bleach.clean(content)
            
            try:
                # Create letter with transaction
                with transaction.atomic():
                    letter = Letter.objects.create(
                        author=request.user,
                        title=title,
                        content=sanitized_content,
                        delivery_date=delivery_date,
                        delivery_attempts=0,  # Initialize delivery attempts
                        last_delivery_attempt=None  # Initialize last attempt
                    )
                    
                    logger.info(f"Successfully created letter:")
                    logger.info(f"Letter ID: {letter.id}")
                    logger.info(f"Author: {letter.author.email}")
                    logger.info(f"Delivery Date (UTC): {letter.delivery_date}")
                    logger.info(f"Is Delivered: {letter.is_delivered}")
                    logger.info(f"Delivery Attempts: {letter.delivery_attempts}")
                    logger.info("=== End Letter Creation Debug ===\n")
                    
                    # Store letter ID in session for confirmation
                    request.session['last_letter_id'] = letter.id
                    
                    return JsonResponse({
                        'message': 'Letter saved successfully',
                        'letter_id': letter.id
                    }, status=201)
            except Exception as e:
                logger.error(f"Database error while creating letter: {str(e)}", exc_info=True)
                return JsonResponse({'error': 'Failed to save letter to database'}, status=500)
                
        except ValueError as e:
            logger.error(f"Invalid date format: {str(e)}")
            return JsonResponse({'error': 'Invalid date format'}, status=400)
            
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data: {str(e)}")
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error saving letter: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Failed to save letter'}, status=500)

@login_required(login_url='/accounts/login/')
def api_letters(request):
    letters = Letter.objects.filter(author=request.user).order_by('delivery_date')
    return JsonResponse({
        'letters': [
            {
                'id': letter.id,
                'title': letter.title,
                'content': letter.content,
                'delivery_date': letter.delivery_date.isoformat(),
                'created_at': letter.created_at.isoformat()
            }
            for letter in letters
        ]
    })

def logout_view(request):
    logout(request)
    return redirect('login')

@csrf_exempt
@require_http_methods(["POST"])
def resend_otp_api(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({'detail': 'Email is required'}, status=400)
            
        try:
            pending_reg = PendingRegistration.objects.get(email=email)
            
            # Generate new OTP
            new_otp = str(random.randint(100000, 999999))
            pending_reg.otp_code = new_otp
            pending_reg.created_at = timezone.now()
            pending_reg.save()
            
            # Update session OTP
            request.session['register_otp'] = new_otp
            
            # Send new OTP email
            send_otp_email(email, new_otp)
            
            return JsonResponse({
                'success': True,
                'message': 'New verification code sent successfully.'
            })
            
        except PendingRegistration.DoesNotExist:
            return JsonResponse({
                'detail': 'No pending registration found for this email.'
            }, status=404)
            
    except Exception as e:
        logger.error(f'Resend OTP error: {str(e)}')
        return JsonResponse({'detail': str(e)}, status=500)

@login_required
def confirmation_view(request):
    return render(request, 'confirmation.html')

def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)

@login_required
def view_letter(request, letter_id):
    try:
        letter = Letter.objects.get(id=letter_id, author=request.user)
        return render(request, 'view_letter.html', {'letter': letter})
    except Letter.DoesNotExist:
        return render(request, '404.html', status=404)
