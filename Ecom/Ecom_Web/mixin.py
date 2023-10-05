from django.core.mail import send_mail 
import random
from django.conf import settings
from smtplib import  SMTPException, SMTPRecipientsRefused
from django.contrib.auth.models import User

from .models import UserProfile



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
