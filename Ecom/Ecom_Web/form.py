from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login
import re
from django.contrib.auth.hashers import check_password


from .models import UserProfile,Address


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label='Email',help_text="required *", widget=forms.TextInput(attrs={'class': 'email form-control', 'placeholder': 'email'}))
    password = forms.CharField(max_length=30, required=True, label='Password', widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder': 'password'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) 
        self.log = kwargs.pop("log" , None)
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
                # print(user)
                if user is None:
                    
                    self.add_error('password', forms.ValidationError('Invalid password.'))
                elif self.log and not user.is_superuser :
                    # print('no authrntiion')
                    self.add_error("username" , "you have no autherization to acess this page")
                elif not user.is_active:
                    # print('block')
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

class ResetPassword(forms.Form):
    password = forms.CharField(max_length=30 ,required=True, label='Password' ,help_text="required *",  widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))
    c_password = forms.CharField(max_length=30 ,required=True, label='Confrim Password'  ,help_text="required *", widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))


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
    

class EditProfileForm(forms.ModelForm):


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
        if self.instance.pk and self.instance.email != email:
            if UserProfile.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already in use.')
        return email



    
class ChangePassword(forms.Form):

    password = forms.CharField(max_length=30 ,required=True, label='Old Password' ,help_text="required *",  widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))
    n_password = forms.CharField(max_length=30 ,required=True, label='New Password' ,help_text="required *",  widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))
    c_password = forms.CharField(max_length=30 ,required=True, label='Confrim New Password'  ,help_text="required *", widget=forms.PasswordInput(attrs={'class': 'password form-control', 'placeholder':'password'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePassword, self).__init__(*args, **kwargs)


    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not check_password(password , self.user.password):
            raise forms.ValidationError("wrong password")
        return password

    def clean_n_password(self): 
        password = self.cleaned_data.get('n_password')
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
        password1 = cleaned_data.get('n_password')
        password2 = cleaned_data.get('c_password')
        
        if password1 and password2 and password1 != password2:
            self.add_error( 'c_password',"New Passwords do not match...")
        
        return cleaned_data


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'village',
            'city',
            'district',
            'pincode',
            'landmark',
            'first_phone_number',
            'second_phone_number',
            'primary_address',
        ]

        widgets = {
            'village': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'village', 'required': 'required'}),
            'city': forms.EmailInput(attrs={'class': 'form-control customclass','placeholder':'city' , 'required': 'required'}),
            'district': forms.TextInput(attrs={'class': 'form-control customclass','placeholder':'district' , 'required': 'required'}),
            'pincode' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'pincode number', 'required': 'required'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control customclass' ,'placeholder':'landmark', 'required': 'required'}),
            'first_phone_number' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'First number', 'required': 'required'}),
            'second_phone_number' : forms.NumberInput(attrs={'class': 'form-control customclass','placeholder':'secondnumber'}),
            'primary_address':forms.CheckboxInput(),

        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(AddressForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        f_number = cleaned_data.get('first_phone_number', '')
        s_number = cleaned_data.get('second_phone_number', '')
        p_number = cleaned_data.get('pincode', '')
        
        # Phone number length validation
        if f_number and len(str(f_number)) != 10:
            self.add_error('first_phone_number', 'Phone number must be 10 digits long.')

        if s_number and len(str(s_number)) != 10:
            self.add_error('second_phone_number', 'Phone number must be 10 digits long.')
        
        if p_number and len(str(p_number)) != 6:
            self.add_error('pincode', 'not a valid pincode.')


        # Set primary_address to True if it's the first address for the user
        user = self.user
        if not cleaned_data.get('primary_address') and not Address.objects.filter(user=user).exists():
            cleaned_data['primary_address'] = True
         
        if not self.instance and Address.objects.filter(village = cleaned_data.get('village', ''),city = cleaned_data.get('city', ''),district = cleaned_data.get('district', ''),pincode = cleaned_data.get('pincode', '')).exists():
            self.add_error('','there is already a address in this same address..')
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        cleaned_data = self.cleaned_data
        user = self.user
        if cleaned_data.get('primary_address') and Address.objects.filter(user=user,primary_address =True).exists():
            Address.objects.filter(user = user).update(primary_address = False)
        instance.user = user
        instance.save()
        return instance