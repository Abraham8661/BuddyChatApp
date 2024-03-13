import random
from django.core.mail import send_mail
from .models import OTP_Manager
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.contrib import messages
from django.shortcuts import redirect, HttpResponseRedirect


def OTP_Generator(receiver_address, username):
    number_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    otp = ""
    for num in range(6):
        password = random.choice(number_list)
        otp += password

    subject = "Account Verification from BuddyChat"
    message = f"""Hi @{username}, you just made a request to change your password!
Your one time password is {otp}
Use it to verify your account. Thank you!
This OTP is valid for just 10 minutes.
    """
    sender_address = "godwindave961@gmail.com"
    send_mail(subject, message, sender_address, [receiver_address], fail_silently=False)
    return otp


def verification_email(request, receiver_address, username):
    # Generate OTP
    otp = OTP_Generator(receiver_address, username)

    # Save OTP to database
    user_instance = User.objects.get(username=username)
    try:
        otp_manager_instance = OTP_Manager.objects.get(user=user_instance)
        otp_manager_instance.otp = otp
        otp_manager_instance.save()
    except:
        OTP_Manager.objects.create(user=user_instance, otp=otp)


def OTP_Expiration_Manager(request, user_instance):
    # OTP expiration after 10 minutes
    try:
        saved_otp = OTP_Manager.objects.get(user=user_instance)
    except:
        saved_otp = ""
    current_time = datetime.now(timezone.utc)
    saved_time = saved_otp.date_sent
    duration = timedelta(minutes=10)
    expiration_time = saved_time + duration
    if current_time >= expiration_time:
        saved_otp.active = False
        saved_otp.save()


def Resend_OTP_Manager(request, username):
    # Generate new OTP
    user_instance = User.objects.get(username=username)
    receiver_address = user_instance.email
    new_otp = OTP_Generator(receiver_address, username)

    # Update OTP Model with the new OTP
    try:
        otp_instance = OTP_Manager.objects.get(user=user_instance)
        saved_otp = otp_instance.otp
    except:
        otp_instance = None
        saved_otp = ""
    saved_otp += new_otp
    otp_instance.save()
