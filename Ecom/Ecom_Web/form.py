from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login
import re


from .models import UserProfile



class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label='Email',help_text="required *", widget=forms.EmailInput(attrs={'class': 'email form-control', 'placeholder': 'email'}))
    password = forms.CharField(max_length=30, required=True, label='Password', widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder': 'password'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) 
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username:
            self.add_error('username', "You must enter the email.")
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.add_error('username', 'Invalid email.')

                return cleaned_data

            if user:
                user = authenticate(username=username, password=password)
                if user is None:
                    self.add_error('password', forms.ValidationError('Invalid password.'))
                elif not user.is_active:
                    self.add_error("username" , "You have been block by super user...")
                else:
                    login(self.request , user)
        return cleaned_data
    

class ProfileForm(forms.ModelForm):
    password = forms.CharField(max_length=30 ,required=True, label='Password' ,help_text="required *",  widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))
    c_password = forms.CharField(max_length=30 ,required=True, label='Confrim Password'  ,help_text="required *", widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.log = kwargs.get('logs',False)
        if self.log:
            kwargs.pop('logs')
        super().__init__(*args, **kwargs)

    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'email' ,'phone_number' ,'gender']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'name', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'form-control customclass','placeholder':'email' , 'required': 'required'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control customclass','placeholder':'pass1' , 'required': 'required'}),
            'phone_number' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'number'}),
            'gender':forms.RadioSelect(attrs={'class': 'radios' , 'required': 'required'},choices=[("male", "Male"), ("female", "Female"), ("other", "Other")])

        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise forms.ValidationError('invaild email eg (example@gmail.com )')
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already in use.')
        return email

    
    def clean_password(self): 
        password = self.cleaned_data.get('password')
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Passwords should contain atleast one upper case.")
    
        # Check for at least one lowercase letter
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Passwords should contain atleast one lower case")
        
        # Check for at least one digit
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Passwords should contain atleast one number.")
        
        # Check for at least one special character using regular expression
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Passwords should contain atleast one special char.")
        
        # If all conditions are met, return True
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('c_password')
        
        if password1 and password2 and password1 != password2:
            self.add_error( 'c_password',"Passwords do not match.")
        
        return cleaned_data
    
    def save(self, commit=True):
        super().save(commit=False)
        # profile = super().save(commit=False)
        # # print("hello")
        # password = self.cleaned_data.get('password')
        # if commit:
        #     user = User.objects.create_user(username=profile.email, password=password , email = profile.email)
        #     profile.user = user
        #     profile.save()
        #     if self.log:
        #         login(self.request , user)
        # return profile