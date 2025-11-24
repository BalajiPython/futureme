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
