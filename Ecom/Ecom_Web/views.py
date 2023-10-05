from django.shortcuts import render,redirect,HttpResponse
from django.views.generic.base import TemplateView
# from django.views import View
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core import signing 
from django.urls import reverse
from django.contrib.auth import authenticate , login
from django.contrib import messages


from . import form
from .models import UserProfile
from .mixin import sendOTP , createUser
# Create your views here.


class HomeTemplate(TemplateView):

    template_name = "user/home.html"


@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def customLogin(request):
    if request.user.is_authenticated:
        return redirect('Ecom:home')
    loginform = form.LoginForm()
    if request.POST.get('signin'):
        loginform = form.LoginForm(request.POST , request = request )
        if loginform.is_valid():
            messages.add_message(request,messages.SUCCESS, f'login sucess {loginform.cleaned_data.get("username")}',extra_tags="Login")
            return redirect('Ecom:home')
    return render (request , "user/login.html" , {'form':loginform})

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def customSignup(request):
    if request.user.is_authenticated:
        return redirect('Ecom:home')
    signUp = form.ProfileForm()
    if request.POST.get('signup'):
        signUp = form.ProfileForm(request.POST,request = request)
        
        if signUp.is_valid():
            signUp.save()
            request.session['new_user'] = signUp.cleaned_data
            email = signing.dumps(signUp.cleaned_data.get('email'))
            return redirect(reverse('Ecom:verify' ,kwargs={'email' :email }))
        
        
    
    
    return render (request , "user/signup.html" , {'signup':signUp}) 

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def verifyEmail(request , email ):
    if request.user.is_authenticated:
        return redirect('Ecom:home')
    
    count = 10
    if request.POST.get('verify'):
        otp = request.POST.get('otp')
        count = int(request.POST.get('counter'))
        print(request.session.get('new_user'))
        if otp == request.session.get('otp'):
            user = createUser(request.session.get('new_user'))
            user = authenticate(request , username = user.username , password = user.password)
            login(request , user)
            return redirect("Ecom:home")
        messages.error(request, 'WORNG OTP')
        
    data,otp = None,None

    try:
        data  = signing.loads(email)
    except signing.BadSignature:
        return redirect('Ecom:signup')
    
    # if  not count <  -1:
    
    #     if data:
    #         otp,status , message = sendOTP(data)
    #     else:
    #         return redirect('Ecom:signup')
        
    #     if not status:
    #         return HttpResponse(f"{message}")
    #     else:
    #         request.session['otp'] = otp
    #         return render(request , 'user/verify.html' , {'uemail' : email , 'countdown' : count})
     
    return render(request , 'user/verify.html' , {'uemail' : email , 'countdown' : count})