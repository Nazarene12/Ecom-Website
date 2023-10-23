from django.core.mail import send_mail 
import random
from django.conf import settings
from smtplib import  SMTPException, SMTPRecipientsRefused
from django.contrib.auth.models import User

from .models import UserProfile

from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.mixins import UserPassesTestMixin



def sendOTP(email):

    otp = str(random.randint(1000,9999))

    subject = 'OTP verification'
    message  = f"Your OTP is {otp}"

    try:
        send_mail(subject , message , settings.EMAIL_HOST_USER , [email])

    except SMTPRecipientsRefused:
        print("invalid email")
        return (otp , False , "invalid email")
    except SMTPException:
        return (otp , False , "server issue")
    except Exception:
        return (otp , False , "error occured")

    return (otp , True , 'success')

def createUser(data):

    user  = User.objects.create_user(username=data.get('email') , password= data.get('password') , email = data.get('email'))
    user.save()
    obj = UserProfile(first_name = data.get('first_name') , last_name = data.get('last_name'),email = data.get('email') , gender = data.get('gender'))
    obj.phone_number = data.get("phone_number")
    obj.user = user
    obj.save()
    return user


def conformationmail(email):

    subject = 'order confrimation'
    message  = f"Your order has been placed"

    try:
        send_mail(subject , message , settings.EMAIL_HOST_USER , [email])

    except SMTPRecipientsRefused:
        print("invalid email")
        return ( False , "invalid email")
    except SMTPException:
        return ( False , "server issue")
    except Exception:
        return ( False , "error occured")

    return ( True , 'success')


class UserPermissionCustomMixin(UserPassesTestMixin):
    def test_func(self):
        if self.request.user.is_authenticated and self.request.user.is_active:
            return True

    def handle_no_permission(self):
        if self.raise_exception or ( self.request.user.is_authenticated and not self.request.user.is_active) or not self.request.user.is_authenticated:
            return redirect('Ecom:login')  # Redirect to login if user is not logged in or raise_exception is True