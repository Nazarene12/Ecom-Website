from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render,redirect,HttpResponse
from django.views.generic.base import TemplateView
# from django.views import View
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core import signing 
from django.urls import reverse ,reverse_lazy
from django.contrib.auth import authenticate , login ,logout
from django.views.generic import ListView , DetailView ,CreateView , UpdateView
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, JsonResponse
import json
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import  cache_control
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.core import serializers
from django.db.models import Sum


from . import form
from .models import UserProfile,UserCart,Address,Order
from .mixin import sendOTP , createUser ,conformationmail
from adminpanel.models import Connector,Category , Brand , Size , Color , Product , ProductImage
# Create your views here.
from .mixin import UserPermissionCustomMixin


        

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class HomeTemplate(TemplateView):
    template_name = "user/home.html"



@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def customLogin(request):
    if request.user.is_authenticated and request.user.is_active:
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
    if request.user.is_authenticated and request.user.is_active:
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
    if request.user.is_authenticated and request.user.is_active :
        
        return redirect('Ecom:home')
    count = 180
    if request.POST.get('verify'):
        otp = request.POST.get('otp')
        count = int(request.POST.get('counter'))
        if otp == request.session.get('otp'):
            if request.GET.get('profile'):
                try:
                    data  = signing.loads(email)
                except signing.BadSignature:
                    return redirect('Ecom:editprofile')
                request.user.username= data
                request.user.email = data
                request.user.save()
                request.user.user.email = data
                request.user.user.save()
                return redirect('Ecom:profile')
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
    if request.user.is_authenticated and request.user.is_active:
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
    if request.user.is_authenticated and request.user.is_active:
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
class ProductList(ListView ):
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


        
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class productDetail(DetailView):
    model = Connector
    template_name = "user/productdetail.html"
    context_object_name = 'product'

    def get_object(self, queryset=None):
        obj = super().get_object()

        product = obj.product

        obj.colors = Connector.objects.filter(product = product).exclude(color = obj.color).values('color__name','image').distinct()

        obj.sizes = Connector.objects.filter(product = product , color = obj.color , count__gt = 0).values_list('size__size',flat=True).order_by('size')
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
    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class CartList(UserPermissionCustomMixin,ListView):

    model = UserCart
    template_name= 'user/cart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        # Specify the default ordering for the queryset
        queryset = UserCart.objects.filter(user = self.request.user , delete_cart = False).order_by('-id')
        return queryset


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class Profile(UserPermissionCustomMixin,DetailView):
    model = User
    template_name = "user/profile.html"
    context_object_name = 'user' 

    def get_object(self, queryset=None):
        return self.request.user 


def FormHandlerCart(request):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:login')
    if request.method == 'POST':
        ids = request.POST.getlist('values')
        request.session['checkout_product'] = ids
        request.session['total_amount'] = request.POST.get('total_price')
        request.session['total_items'] = request.POST.get('total_items')
        return JsonResponse({'success':True})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def CheckOut(request):
    previous_path = request.session.get('previous_url',None)
    current_path = request.session.get('current_url',None)
    print(previous_path,current_path)
    # print(request.META.get('HTTP_REFERER'))
    # if previous_path:
    #     print("entered")
    #     return redirect(previous_path)
    if not request.user.is_authenticated or not request.user.is_active:
        return redirect('Ecom:home')
    data = UserCart.objects.filter(id__in = request.session['checkout_product'])
    address = Address.objects.filter(user = request.user)

    if request.method == 'POST':
        address = request.POST.get('address')
        obj = Order()
        obj.user = request.user
        obj.address = Address.objects.get(id = address)
        
        obj.total_price = request.session.get('total_amount')
        obj.total_item = request.session.get('total_items')
        obj.payment_method = 'cash_on_delivery'
        obj.status = 'pending'
        obj.save()
        total_count = 0
        for i in data:
            # print(i.connect)
            obj.products.add(i.connect.id)
            i.connect.count = i.connect.count-i.quantity
            i.connect.sale = i.connect.sale + i.quantity
            total_count = total_count + i.connect.count
            i.connect.save()
            i.delete_cart = True
            i.save()
        # if total_count == 0:

        obj.save()
        conformationmail(request.user.email)
        return redirect('Ecom:successpage')


    return render(request,"user/checkout.html" ,{'products':data , 'total_amount':request.session['total_amount'] , 'address':address})

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def SuccessPage(request):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:login')
    return render(request,'user/successpage.html')

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class UserOrder(UserPermissionCustomMixin,ListView):

    model = Order
    template_name = 'user/userorder.html'
    context_object_name = 'orders'

    def get_queryset(self) :
        return Order.objects.filter(user = self.request.user)

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def logouts(request):
    logout(request)
    return redirect("Ecom:home")
      

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def UserProfileUpdate(request):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:home')
    userForm = form.EditProfileForm(instance=request.user.user)
    if request.method == 'POST':
        userForm = form.EditProfileForm(request.POST,instance=request.user.user)
        if userForm.is_valid():
            # print(request.user.user.email,userForm.cleaned_data['email'])
            if request.user.email != userForm.cleaned_data['email']:
                user = userForm.save(commit=False)
        
                user.first_name = userForm.cleaned_data.get('first_name')
                user.last_name = userForm.cleaned_data.get('last_name')
                user.phone_number = userForm.cleaned_data.get('phone_number')
                user.gender = userForm.cleaned_data.get('gender')
                
                user.save()
                email = signing.dumps(userForm.cleaned_data.get('email'))
                return redirect(reverse('Ecom:verify' ,kwargs={'email' :email })+'?profile=True')
            userForm.save()
            return redirect('Ecom:profile')
    return render(request , 'user/userprofileedit.html' , {'form':userForm})


@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def UserChangePassword(request):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:home')
    userForm = form.ChangePassword(user= request.user)

    if request.method == 'POST':
        userForm = form.ChangePassword(request.POST,user = request.user)
        if userForm.is_valid():
            user = User.objects.get(id = request.user.id)
            user.set_password(userForm.cleaned_data['n_password'])
            user.save()
            return redirect('Ecom:profile')

    return render(request , 'user/UserChangePassword.html' , {'form':userForm})
    
@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def UserAddAdress(request):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:home')
    
    userForm = form.AddressForm(user = request.user)

    if request.method == 'POST':
        userForm = form.AddressForm(request.POST,user = request.user)
        if userForm.is_valid():
            userForm.save()
            if request.GET.get('next'):
                return redirect(request.GET.get('next'))
            return redirect('Ecom:profile')
    return render(request,'user/useraddressadd.html',{'form':userForm})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class UpdateAdress(UserPermissionCustomMixin,UpdateView):

    model = Address
    template_name ='user/useraddressadd.html'
    form_class = form.AddressForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        else:
            return reverse('Ecom:profile')

@method_decorator(login_required, name='get')
class GetProductData (UserPermissionCustomMixin,View):

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
        
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class AddCart(UserPermissionCustomMixin,CreateView):

    http_method_names=['get']

    def get(self, request, *args, **kwargs):
        try:
            connect = Connector.objects.get(id = request.GET.get('pk'))
            if UserCart.objects.filter(user = request.user , connect =connect , delete_cart = False).exists():
                
                obj = UserCart.objects.get(user = request.user , connect =connect , delete_cart = False)
                if obj.quantity == 5:
                    return JsonResponse({'success':False , 'error':'reached max..'})
                if( obj.quantity + int(request.GET.get('quantity'))) >= 5 :
                    obj.quantity = 5
                    obj.save()
                    return JsonResponse({'success':True })
                obj.quantity = obj.quantity + int(request.GET.get('quantity'))
                obj.save()
            else:
                obj=UserCart(user=request.user)
                obj.connect = connect
                obj.quantity = request.GET.get('quantity')
                obj.save()
            return JsonResponse({'success':True})
        except:
            return JsonResponse({'success':False, 'error':'invalid'})
           
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class UpdateCart(UserPermissionCustomMixin,UpdateView):

    http_method_names = ['post']

    def post(self, *args, **kwargs):
        try:
            # print(self.request.PUT)
            cart = UserCart.objects.get(id = self.request.POST.get('pk'))
            action= self.request.POST.get('action')

            if action == '1':
                cart.quantity = cart.quantity  + 1
            if action == '0':
                cart.quantity = cart.quantity  - 1
            cart.save()
            return JsonResponse({'success': True})

        except cart.DoesNotExist:
            return JsonResponse({'success': False})

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')     
class DeleteCart(UserPermissionCustomMixin,UpdateView):

    http_method_names = ['post']

    def post(self, *args, **kwargs):
        try:
            # print(self.request.PUT)
            cart = UserCart.objects.get(id = self.request.POST.get('pk'))
            cart.delete_cart = True
            cart.save()
            return JsonResponse({'success': True})

        except cart.DoesNotExist:
            return JsonResponse({'success': False})

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')       
class SetPrimary(UserPermissionCustomMixin,CreateView):

    http_method_names=['get']

    def get(self, request, *args, **kwargs):
        try:
            address = Address.objects.get(id = kwargs.get('pk') )
            user = address.user
            print(address)
            old_address = Address.objects.get(user = user , primary_address = True)
            old_address.primary_address = False
            old_address.save()
            address.primary_address = True
            address.save()
            return JsonResponse({'success':True})
        except Address.DoesNotExist :

            return JsonResponse({'success':False, 'error':'invalid id'})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')  
class DeleteAddress(UserPermissionCustomMixin,CreateView):

    http_method_names=['get']

    def get(self, request, *args, **kwargs):
        try:
            address = Address.objects.get(id = kwargs.get('pk') )
            if address.primary_address and Address.objects.filter(user = address.user).exists():
                new_address = Address.objects.filter(user = address.user).order_by('-id').first()
                new_address.primary_address = True
                new_address.save()
                address.delete()
                return JsonResponse({'success':True , 'next':new_address.id})
            address.delete()
            return JsonResponse({'success':True})
        except Address.DoesNotExist :

            return JsonResponse({'success':False, 'error':'invalid id'})




@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class CancelOrder(UserPermissionCustomMixin,UpdateView):

    http_method_names = ['post','get']

    def get(self, request, *args, **kwargs) :
        try:
            order = Order.objects.get(id = kwargs.get('pk') )
            order.status = 'cancel'
            order.save()
            return redirect('Ecom:userorder')

        except order.DoesNotExist:
            return JsonResponse({'success': False})

    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(id = kwargs.get('pk') )
            order.status = 'cancel'
            order.save()
            return JsonResponse({'success': True })

        except order.DoesNotExist:
            return JsonResponse({'success': False})