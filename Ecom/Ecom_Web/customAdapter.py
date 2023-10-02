from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import UserProfile  # Import your UserProfile model


import requests
from django.core.files import File
from tempfile import NamedTemporaryFile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # Call the parent class method to create the user
        user = super().save_user(request, sociallogin, form)
        # Check if the user doesn't already have a profile
        if not hasattr(user, 'userprofile'):
            # Create a UserProfile instance and populate it with data
            extra_data = sociallogin.account.extra_data
            # picture_url = extra_data.get('picture', None)  # Assuming the key for the picture URL in extra_data is 'picture'

            profile_data = {
                'user': user,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                # Populate the 'picture' field from extra_data
                # Exclude gender and phone_number fields
            }
            user.username = user.email
            user.save()
            user_profile = UserProfile.objects.create(**profile_data)
            download_and_save_image(user_profile, extra_data.get('picture'))

        return user

def download_and_save_image(user_profile, image_url):
    # Send an HTTP GET request to download the image
    response = requests.get(image_url)

    if response.status_code == 200:
        # Create a temporary file to store the image
        img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(response.content)
        img_temp.flush()

        # Save the temporary image file to the ImageField
        user_profile.picture.save(f"{user_profile.user.username}_profile.jpg", File(img_temp), save=True)