from typing import Any
from django.shortcuts import render,redirect,HttpResponse
from django.views.generic.base import TemplateView
# from django.views import View
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core import signing 
from django.urls import reverse
from django.contrib.auth import authenticate , login ,logout
from django.views.generic import ListView , DetailView ,CreateView
from django.contrib import messages
from django.http import JsonResponse
import json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import  cache_control
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core import serializers


from . import form
from .models import UserProfile
from .mixin import sendOTP , createUser
from adminpanel.models import Connector,Category , Brand , Size , Color , Product , ProductImage
# Create your views here.

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
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
    
    count = 180
    if request.POST.get('verify'):
        otp = request.POST.get('otp')
        count = int(request.POST.get('counter'))
        if otp == request.session.get('otp'):
            if request.GET.get("forgot"):
                return redirect('Ecom:resetpassword')
            user = createUser(request.session.get('new_user'))            
            login(request , user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect("Ecom:home")
        messages.error(request, 'WORNG OTP')
        
    data,otp = None,None

    try:
        data  = signing.loads(email)
    except signing.BadSignature:
        return redirect('Ecom:signup')
    
    if  count ==  180:
    
        if data:
            otp,status , message = sendOTP(data)
        else:
            return redirect('Ecom:signup')
        
        if not status:
            return HttpResponse(f"{message}")
        else:
            request.session['otp'] = otp
            return render(request , 'user/verify.html' , {'uemail' : email , 'countdown' : count})
     
    return render(request , 'user/verify.html' , {'uemail' : email , 'countdown' : count})

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def forgot(request):
    if request.user.is_authenticated:
        return redirect('Ecom:home')
    error=''
    if request.method == 'POST':
        email = request.POST.get("email")
        if User.objects.filter(username = email).exists():
            request.session['forgot_id'] = User.objects.get(username = email).id
            email = signing.dumps(email)
            return redirect(reverse('Ecom:verify' ,kwargs={'email' :email })+'?forgot=True')
        error="invalid email"
    return render(request,'user/forgot.html' , {'error':error})

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def resetpassword(request):
    if request.user.is_authenticated:
        return redirect('Ecom:home')
    resetform = form.ResetPassword()
    if request.POST.get('restform'):
        resetform = form.ResetPassword(request.POST)
        if resetform.is_valid():
            user = User.objects.get(id = request.session['forgot_id'])
            user.set_password(resetform.cleaned_data['password'])
            user.save()
            messages.add_message(request,messages.SUCCESS, f'login sucess {user.username}',extra_tags="Login")
            return redirect('Ecom:login')
    return render(request,'user/resetpassword.html',{'form':resetform})

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class ProductList(ListView):
    model = Product
    template_name= 'user/product.html'
    paginate_by=2
    context_object_name = 'products'

    def get_queryset(self):
        # Specify the default ordering for the queryset
        queryset = Product.objects.filter(active = True).order_by('id')

        

        # Apply filters based on query parameters if they exist
        if self.request.GET.get('price'):
            queryset = queryset.filter(price__lt=self.request.GET.get('price'))

        if self.request.GET.get('brand'):
            queryset = queryset.filter(brand__id=self.request.GET.get('brand'))

        if self.request.GET.get('category'):
            queryset = queryset.filter(category__id=self.request.GET.get('category'))
        
        for each in queryset:
            each.varient = each.detail_product.filter(first_preference = True).first()

        if self.request.GET.get('color'):
            queryset = queryset.filter(detail_product__color__id=self.request.GET.get('color')).distinct()

            for each in queryset:
                each.varient = each.detail_product.filter(color__id = self.request.GET.get('color')).first()

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        context['brand'] = Brand.objects.all()
        context['color'] = Color.objects.all()

        # Add filter parameters to context
        context['price_param'] = self.request.GET.get("price")
        context['brand_param'] = int(self.request.GET.get("brand")) if self.request.GET.get("brand") else None
        context['category_param'] = int(self.request.GET.get("category")) if self.request.GET.get("category") else None
        context['color_param'] = int(self.request.GET.get("color")) if self.request.GET.get("color") else None

        return context
    
    

    # def get_queryset(self):

    #     return Connector.objects.filter(first_preference = True)

def productFilter(request):
    if request.method =='POST':

        try:
            data = json.loads(request.body)
            
            filter_value = data.get('filter_value')
            
            result = Connector.objects.all()

            if 'price' in filter_value:
                for i in filter_value['price']:
                    result = result.select_related('product').filter(product__price__lt = i)
            if 'brand' in filter_value:
                for i in filter_value['brand']:
                    result = result.select_related('product').filter(product__brand__id = i)

            if 'category' in filter_value:
                for i in filter_value['category']:
                    result = result.select_related('product').filter(product__category__id = i)
            
            if 'color' in filter_value:
                for i in filter_value['color']:
                    result = result.select_related('product').filter(color__id = i)

            print(result)
            products_json = serializers.serialize('json', result)
            return JsonResponse({'success':True,'products': products_json})

        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON data'})
        
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class productDetail(DetailView):
    model = Connector
    template_name = "user/productdetail.html"
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object()

        product = obj.product

        obj.colors = Connector.objects.filter(product = product).exclude(color = obj.color).values('color__name','image').distinct()

        obj.sizes = Connector.objects.filter(product = product , color = obj.color).values_list('size__size',flat=True).order_by('size')
        return obj
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        size_dict ={}
        obj = self.get_object()
        product = obj.product
        values = Connector.objects.filter(product = product , color = obj.color).values_list('size__size','id').order_by('size')
        for i in values:
            size_dict[i[0]] = i[1]
        context['all_size'] = Size.objects.all()
        context['size_id'] = size_dict
        return context

    

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def logouts(request):
    logout(request)
    return redirect("Ecom:home")
      


@method_decorator(login_required, name='get')
class GetProductData (View):

    http_method_names=['get']

    def get(self, request, *args, **kwargs):

        try:
            image = ProductImage.objects.get(id = kwargs['pk'])
            obj = Connector.objects.filter(image = image).first()
            all_size = Connector.objects.filter(product = obj.product , color=obj.color).values_list('size__size','id').order_by('size')
            size_dict={}
            for eachsize in all_size:
                size_dict[eachsize[0]] = eachsize[1]
            print(size_dict)
            # serialized_data = serializers.serialize('json', all_size)
            return JsonResponse({
                                'success':True ,
                                'front_image' : obj.image.front_image.url ,
                                'back_image' : obj.image.back_image.url,
                                'side_image':obj.image.side_image.url,
                                'normal_image':obj.image.normal_image.url,
                                'size_id':size_dict
                                })
        except Connector.DoesNotExist:
            return JsonResponse({'success':False})