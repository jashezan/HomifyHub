import os
from twilio.rest import Client
from django.conf import settings
from django.core.cache import cache
import requests
from django.core.files.storage import default_storage
from django.utils.crypto import get_random_string

def send_otp(user):
    """
    Sends OTP to user's phone number via Twilio.
    Stores OTP in cache for verification (5-minute expiry).
    Args:
        user: User instance with phone number.
    Returns:
        bool: True if sent, False if failed.
    """
    if not user.phone:
        return False
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        otp = get_random_string(length=6, allowed_chars='0123456789')
        cache.set(f'otp_{user.id}', otp, timeout=300)  # 5 minutes
        message = client.messages.create(
            body=f'Your HomifyHub OTP is {otp}',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=user.phone
        )
        return True
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return False

def verify_otp(user, otp):
    """
    Verifies OTP against cached value.
    Args:
        user: User instance.
        otp: OTP string provided by user.
    Returns:
        bool: True if valid, False otherwise.
    """
    cached_otp = cache.get(f'otp_{user.id}')
    return cached_otp == otp

def imgbb_upload(file):
    """
    Uploads file to imgbb and returns URL.
    Args:
        file: File object (e.g., from form).
    Returns:
        str: URL of uploaded image or None if failed.
    """
    try:
        url = 'https://api.imgbb.com/1/upload'
        payload = {'key': settings.IMGBB_API_KEY}
        files = {'image': default_storage.open(file.name, 'rb')}
        response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            return response.json()['data']['url']
        return None
    except Exception as e:
        print(f"Error uploading to imgbb: {e}")
        return None

def send_notification(user, message):
    """
    Sends notification to user (e.g., via email or SMS).
    Currently logs to console; extend for email/SMS.
    Args:
        user: User instance.
        message: Notification message.
    """
    print(f"Notification to {user.email}: {message}")
    # Extend with email (django.core.mail) or SMS (Twilio) as needed
    # Example: send_mail(subject, message, from_email, [user.email])