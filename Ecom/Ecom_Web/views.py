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

from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils.timezone import now

# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync




from . import form
from .models import UserProfile,UserCart,Address,Order,ProductOrdered,UserWishList,Coupon,UserWallet
from .mixin import sendOTP , createUser ,conformationmail
from adminpanel.models import Connector,Category , Brand , Size , Color , Product , ProductImage ,Ratting,Comment,Transaction
# Create your views here.
from .mixin import UserPermissionCustomMixin

import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import sys

def write_to_pipe():
    try:
        # Code that writes to the pipe
        # ...
        sys.stdout.flush()  # Flush the output to the pipe
    except BrokenPipeError:
        # Handle the broken pipe error
        # Restart or resume execution here
        print("Pipe is broken. Restarting...")
        write_to_pipe()  # Restart the function

def RestartPipe(request):
    write_to_pipe()
    return JsonResponse({'success' :True})

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))       

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
        queryset = Product.objects.filter(active = True , category__active = True , brand__active = True).order_by('id')

        if self.request.GET.get('name'):
            queryset  = queryset.filter(name__icontains = self.request.GET.get('name'))

        # Apply filters based on query parameters if they exist
        if self.request.GET.get('price') and not self.request.GET.get('start_price'):
            queryset = queryset.filter(price__lt=self.request.GET.get('price')).order_by('price')
        if not self.request.GET.get('price') and self.request.GET.get('start_price'):
            queryset = queryset.filter(price__gt=self.request.GET.get('start_price')).order_by('price')
        if self.request.GET.get('price') and self.request.GET.get('start_price'):
            queryset = queryset.filter(price__lt=self.request.GET.get('price') , price__gt=self.request.GET.get('start_price')).order_by('price')

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
        context['category'] = Category.objects.filter(active = True)
        context['brand'] = Brand.objects.filter(active = True)
        context['color'] = Color.objects.filter(active = True)
        if self.request.user.is_authenticated:
            context['liked_products'] = UserWishList.objects.filter(user = self.request.user).values_list('product' , flat=True)
        else:
            context['liked_products'] = 'empty'
        # Add filter parameters to context
        context['price_param'] = self.request.GET.get("price")
        context['price_start_param'] = self.request.GET.get('start_price')
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

        obj.colors = Connector.objects.filter(product = product,active=True).exclude(color = obj.color).values('color__name','image').distinct()

        obj.sizes = Connector.objects.filter(product = product ,active=True, color = obj.color ).values_list('size__size',flat=True).order_by('size')
        return obj
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        size_dict ={}
        obj = self.get_object()
        product = obj.product
        values = Connector.objects.filter(product = product , color = obj.color , active=True).filter(count__gt = 1).values_list('size__size','id').order_by('size')
        print(values)
        for i in values:
            size_dict[i[0]] = i[1]
        context['all_size'] = Size.objects.filter(active = True)
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
        for i in queryset:
            if i.quantity > i.connect.count:
                i.quantity = i.connect.count
                i.save()
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['coupons'] = Coupon.objects.filter(expire_date__gte= now())
        return context


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class Profile(UserPermissionCustomMixin,DetailView):
    model = User
    template_name = "user/profile.html"
    context_object_name = 'user' 

    def get_object(self, queryset=None):
        return self.request.user 

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        if not UserWallet.objects.filter(user = self.request.user).exists():
            obj = UserWallet(user=self.request.user)
            obj.save()
            context['wallet'] = obj
        else:
            context['wallet'] = UserWallet.objects.get(user = self.request.user)
        return context
    
@csrf_exempt
def AddWallet(request):
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount'))
            wallet = None
            if UserWallet.objects.filter(user = request.user).exists():
                wallet = UserWallet.objects.get(user = request.user)
            else:
                wallet = UserWallet(user = request.user)
            
            wallet.balance = wallet.balance + amount
            wallet.save()
            transaction = Transaction(user = request.user , transaction_type="Credit" , amount =  amount)
            transaction.save()
            return JsonResponse({'success':True})   
        except UserWallet.DoesNotExist:
            return JsonResponse({'success' : False})
        
    return render(request , 'user/addwallet.html')

@csrf_exempt
def create_razerpay_order(request):
    if request.method == "POST":
        try:
            amount = int(request.POST.get('amount')) * 100  # Convert to paise           
            data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
            order = razorpay_client.order.create(data=data)
            # print('done')
            return JsonResponse({'success' : True ,"order":order})
        except Exception as e:
            return JsonResponse({'error': str(e)})

@csrf_exempt
def RazerPaymentHandler(request):

    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }


            
            try:
                razorpay_client.utility.verify_payment_signature(params_dict)
            except razorpay.errors.SignatureVerificationError:

                return JsonResponse({'success':False ,'error':'unauthorized payments to process'})
            
            return JsonResponse({'success':True})
        
        except:
            return JsonResponse({'success':False ,'error':'error in transaction try again later'})
            

            

def FormHandlerCart(request):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:login')
    if request.method == 'POST':
        ids = request.POST.getlist('values')
        request.session['checkout_product'] = ids
        request.session['total_amount'] = request.POST.get('total_price')
        request.session['total_items'] = request.POST.get('total_items')
        request.session['coupon'] = request.POST.get('coupon')
        return JsonResponse({'success':True})

from django.db.models import Q

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def CheckOut(request):
    previous_path = request.session.get('previous_url',None)
    current_path = request.session.get('current_url',None)
    
    print(previous_path , current_path)

    if not previous_path:
        return redirect('Ecom:home')

    if not request.user.is_authenticated or not request.user.is_active:
        return redirect('Ecom:home')
    coupon_id = request.session.get('coupon' ,None)
    coupon_discount=0
    if coupon_id != '0':
        coupon = Coupon.objects.get(pk = coupon_id)
        coupon_discount = coupon.amount_to_reduce
    data = UserCart.objects.filter(id__in = request.session['checkout_product'])
    
    address = Address.objects.filter(user = request.user)
    max_retail_price = data.aggregate(total_price=Sum(F('connect__product__maximum_retail_price') * F('quantity')))['total_price']
    discount_price = data.aggregate(total_price=Sum(F('connect__product__price') * F('quantity')))['total_price']
    discount_percentage = 100 -( (discount_price/max_retail_price )*100)
    discount_percentage = round(discount_percentage,2)

    if request.method == 'POST':
        try:
            payment_method  = request.POST.get('payment_method')
            if payment_method == '3':
                if UserWallet.objects.filter(user = request.user).exists():
                    obj1 = UserWallet.objects.get(user = request.user)
                    if obj1.balance >= int(request.session.get('total_amount')):
                        obj1.balance -= int(request.session.get('total_amount'))
                        obj1.save()
                        transaction = Transaction(user = request.user , transaction_type="Debit" , amount = int(request.session.get('total_amount')))
                        transaction.save()
                    else:
                        return JsonResponse({'error':True,'account':False , 'amount' : True})
                else:
                    return JsonResponse({'error':True,'account':True})
            address = request.POST.get('address')
            obj = Order()
            obj.user = request.user
            obj.address = Address.objects.get(id = address)
            
            obj.total_price = request.session.get('total_amount')
            obj.total_item = request.session.get('total_items')
            
            if int(coupon_id) != 0:
                coupon = Coupon.objects.get(pk = coupon_id)
                obj.coupon = coupon
                coupon.maximum_apply = coupon.maximum_apply -1
                coupon.save()
            
            if payment_method =='1':

                obj.payment_method = 'cash_on_delivery'

            elif payment_method == '3':
                obj.payment_method = 'wallet'
            
            else:
                obj.payment_method = 'online'
            obj.status = 'pending'
            obj.save()
            for i in data:
                productCover = ProductOrdered(products =i.connect , quantity = i.quantity , total_price =  i.connect.product.price * i.quantity )
                productCover.save()
                obj.product_cover.add(productCover)
                i.connect.count = i.connect.count-i.quantity
                i.connect.sale = i.connect.sale + i.quantity
                i.connect.save()
                
                        
                i.delete_cart = True
                i.save()

            obj.save()
            
            conformationmail(request.user.email)
            messages.success(request, 'success')

            # channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(
            #     'admin_group',
            #     {
            #         'type': 'admin_message',
            #         'message': json.dumps({
            #             'message': 'A new order has been placed.'
            #         })
            #     }
            # )


            return JsonResponse({'success':True , 'pk' : obj.pk})
        except:
            return JsonResponse({'success':False })
        
        # return redirect('Ecom:successpage',pk=obj.pk)

    return render(request,"user/checkout.html" ,{'products':data , 'total_amount':request.session['total_amount'] ,'mrp':max_retail_price,'coupon' : coupon_discount,'dp':discount_percentage, 'address':address})





def OnlinePayment(request , pk):
    order_product  = Order.objects.get(pk = pk)
    
    payment = razorpay_client.order.create({'amount':int(order_product.total_price)*100 , 'currency' : 'INR','payment_capture': 0})
    context = {}
    context['callback_url'] = reverse('Ecom:paymenthandler',kwargs={'pk':pk})
    # context['callback_url'] =pk
    return render(request , 'user/payment.html',{'payment' : payment , 'context':context})

@csrf_exempt
def PaymentHandler(request , pk):
    order_product  = Order.objects.get(pk = pk)
    if request.method == "POST":
        try:
            
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # print(params_dict)
 
            # verify the payment signature.
            result = razorpay_client.utility.verify_payment_signature(
                params_dict)
            if result is not None:
                amount = int(order_product.total_price)*100 
                try:
                    # capture the payemt
                    razorpay_client.payment.capture(payment_id, amount)
 
                    # render success page on successful caputre of payment
                    return redirect('Ecom:successpage',pk=pk)
                except:
                    order_product.delete()
                    # if there is an error while capturing payment.
                    return render(request, 'user/paymentfail.html')
            else:
                order_product.delete()
                # if signature verification fails.
                return render(request, 'user/paymentfail.html')
        except:
            order_product.delete()
            # if we don't find the required parameters in POST data
            return render(request, 'user/paymentfail.html')



@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class InvoiceTemplate(TemplateView):
    template_name = "user/invoice.html" 

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        context['order'] = Order.objects.get(pk = kwargs['pk'])
        return context

def render_pdf_view(request , pk):
    
    template_path = 'user/invoice.html'
    order = Order.objects.get(pk = pk)
    context = {'order': order}
   
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response ,encoding='UTF-8')
    # if error then show some funny view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def SuccessPage(request,pk):
    if not request.user.is_authenticated and not request.user.is_active:
        return redirect('Ecom:login')
    # order_product = Order.objects.get(pk = pk)
    return render(request,'user/successpage.html' , {'pk_id':pk})


from django.db.models import F, ExpressionWrapper, IntegerField
from django.db.models.functions import Now,Trunc
from django.db import models

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class UserOrder(UserPermissionCustomMixin,ListView):

    model = Order
    template_name = 'user/userorder.html'
    context_object_name = 'orders'

    def get_queryset(self) :
        orders = Order.objects.filter(user = self.request.user).order_by('-id')
        for i in orders:
            i.days_since_order = ( now().date() - i.order_date.date() ).days
        return orders
    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class UserWishlist(UserPermissionCustomMixin,ListView):

    model = UserWishList
    template_name = 'user/userwishlist.html'
    context_object_name = 'wishlist'

    def get_queryset(self) :

        queryset = UserWishList.objects.filter(user = self.request.user , product__active = True , product__category__active = True , product__brand__active = True)
        for each in queryset:
            each.product.varient = each.product.detail_product.filter(first_preference = True).first()
        
        return queryset

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
            all_size = Connector.objects.filter(product = obj.product,active=True , color=obj.color).values_list('size__size','id').order_by('size')
            size_dict={}
            for eachsize in all_size:
                size_dict[eachsize[0]] = eachsize[1]
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
                # if( obj.quantity + int(request.GET.get('quantity'))) >= 5 and connect.count >=5 :
                #     obj.quantity = 5
                #     obj.save()
                #     return JsonResponse({'success':True })
                # if ( obj.quantity + int(request.GET.get('quantity'))) >= 5 and connect.count < 5:
                #     obj.quantity = connect.count
                #     obj.save()
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
            varient = Connector.objects.get(id = cart.connect.id)
            action= self.request.POST.get('action')

            if action == '1':
                if cart.quantity + 1 <= varient.count :
                    cart.quantity = cart.quantity  + 1
                else:
                    return JsonResponse({'success':True , 'limit' : True})
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

    http_method_names = ['post']

    
    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(id = kwargs.get('pk') )
            order.status = 'cancel'
            for i in order.product_cover.all():
                obj = i.products
                obj.count += 1
                obj.sale -= 1
                obj.save()
            if UserWallet.objects.filter(user = order.user).exists():
                wallet = UserWallet.objects.get(user = order.user)
            else:
                wallet = UserWallet(user = order.user)
            wallet.balance = wallet.balance + order.total_price
            wallet.save()
            order.save()
            return JsonResponse({'success': True })

        except order.DoesNotExist:
            return JsonResponse({'success': False})
        

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class ReturnOrder(UserPermissionCustomMixin,UpdateView):

    http_method_names = ['post']

    
    def post(self, *args, **kwargs):
        try:
            order = Order.objects.get(id = kwargs.get('pk') )
            order.return_product = True
            for i in order.product_cover.all():
                obj = i.products
                obj.count += 1
                obj.sale -= 1
                obj.save()
            if UserWallet.objects.filter(user = order.user).exists():
                wallet = UserWallet.objects.get(user = order.user)
            else:
                wallet = UserWallet(user = order.user)
            wallet.balance = wallet.balance + order.total_price
            wallet.save()
            order.save()
            return JsonResponse({'success': True })

        except order.DoesNotExist:
            return JsonResponse({'success': False})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class LikeProduct(UserPermissionCustomMixin,UpdateView):

    http_method_names = ['post']

    def post(self, *args, **kwargs):
        try:

            product = Product.objects.get(pk =self.request.POST.get('pk'))
            if UserWishList.objects.filter(product= product , user = self.request.user).exists():
                obj = UserWishList.objects.get(product= product , user = self.request.user)
                obj.delete()
                return JsonResponse({'success': True , 'liked':False})
            else:
                obj = UserWishList(product= product , user = self.request.user)
                obj.save()
                return JsonResponse({'success': True , 'liked':True})

        except Product.DoesNotExist:
            return JsonResponse({'success': False})
        
from datetime import datetime
      
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
class CouponManager(UserPermissionCustomMixin,UpdateView):

    http_method_names = ['post']

    def post(self, *args, **kwargs):
        try:

            # print(self.request.POST.get('code'))
            if Coupon.objects.filter( coupon_code=self.request.POST.get('code')).exists():
                code = Coupon.objects.get( coupon_code=self.request.POST.get('code'))
                amount = int(self.request.POST.get('amount'))
                current_date = datetime.now().date()
                if current_date > code.expire_date:
                    return JsonResponse({'success': True , 'coupon':False , 'error' : 'Coupon Expired'})
                if code.maximum_apply <=0:
                    return JsonResponse({'success': True , 'coupon':False , 'error' : 'Coupon Maximum Reached'})
                if code.minimum_purchase > amount:
                    return JsonResponse({'success': True , 'coupon':False , 'error' : f'Max Purchase {code.minimum_purchase}'})
                code.maximum_apply += 1
                code.save()
                return JsonResponse({'success': True , 'coupon':True , 'dicount' : code.amount_to_reduce , 'couponId':code.id})
            else:
                return JsonResponse({'success': True , 'coupon':False , 'error' : 'Wrong Coupon'})

        except Coupon.DoesNotExist:
            return JsonResponse({'success': False})
        
@csrf_exempt
def ProfileImage(request):

    if request.method == 'POST':
        print('hi')
        uploaded_file = request.FILES['file']
        obj = UserProfile.objects.get(user = request.user)
        obj.picture = uploaded_file
        obj.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})


from django.db.models import Avg

def Ratting_Product(request , pk):
    if request.method == 'POST':
        try:
            value = request.POST.get('value')
            order  = ProductOrdered.objects.get(id = pk)
            order.rating = value
            order.save()
            
            obj = Product.objects.get(id = order.products.product.id)
            rate = Ratting(product =obj , rating = value )
            rate.save()
            average_rating = Ratting.objects.filter(product=order.products.product).aggregate(Avg('rating'))['rating__avg']
            print(average_rating)
            order.products.product.rating = average_rating
            order.products.product.save()
            return JsonResponse({'success' :True})
        except:
            return JsonResponse({'success':False})
        
def Comment_Product(request , pk):

    if request.method == 'POST':

        try:
            value = request.POST.get('value')
            product = Product.objects.get(id = pk)
            obj = Comment(product = product , comment = value)
            obj.save()
            return JsonResponse({'success':True})
        except:
            return JsonResponse({'success' : False})
        
        # @cache_control(no_cache=True, must_revalidate=True, no_store=False)
