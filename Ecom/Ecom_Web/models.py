
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=False , null=False  , help_text='required*')
    last_name = models.CharField(max_length=30 ,blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField( blank=False , null=False , help_text='required*')
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], blank=False , null=False  ,default='male')
    picture = models.ImageField(upload_to="profile/", blank=True, null=True)
    # Add other fields as needed for your user profile

    def __str__(self):
        return self.user.username
