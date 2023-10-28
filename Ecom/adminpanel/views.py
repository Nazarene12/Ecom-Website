from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.shortcuts import render
from django.shortcuts import render,redirect,HttpResponse
from django.views.generic.base import TemplateView
from django.views import View
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core import signing 
from django.urls import reverse , reverse_lazy
from django.contrib.auth import authenticate , login ,logout
from django.contrib import messages
from django.views.generic import ListView , DetailView ,CreateView , UpdateView
from django.views.generic.edit import ModelFormMixin
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.forms import formset_factory

from django.db.models import Count
from django.conf import settings
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.templatetags.static import static



from Ecom_Web import form
from.forms import CategoryForm,ProductForm,SizeCountForm,UpdateProductVarient,UpdatedProductAddForm,VarientForm,VarientCountFormSetFactory,SizeCountFormSetFactory,VarientCountColorFormSet,SizeCountFormSet, AddAditionVarientForm,AddAditionVarientColorForm,OredrFormStatus
from Ecom_Web.models import UserProfile,Order,Coupon,UserWallet
from .models import Category,Product,Connector,ProductImage


from django.db.models import Count
from django.db.models.functions import TruncMonth
# Create your views here.

from django.contrib.auth.mixins import UserPassesTestMixin

class SuperUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect('Ecom:home')  # Redirect to home if user is not a superuser
        else:
            return redirect('admins:login') 

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def AdminLogin(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('Ecom:home')
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admins:home')

    loginform = form.LoginForm(request.POST or None , request = request , log="admin")
    if request.POST.get('signin') and loginform.is_valid():
        messages.add_message(request,messages.SUCCESS, f'login sucess {loginform.cleaned_data.get("username")}',extra_tags="Login")
        return redirect('admins:home')

    return render (request , 'admin/login.html', {'form':loginform})

def get_orders_per_month(year):
    orders_per_month = Order.objects.filter(
        order_date__year=year
    ).annotate(
        month=TruncMonth('order_date')
    ).values(
        'month'
    ).annotate(
        count=Count('pk')
    ).order_by(
        'month'
    )

    months = {
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0,
    }

    # Update the count for each month
    for order in orders_per_month:
        month = order['month'].strftime('%B')
        count = order['count']
        months[month] = count

    return list(months.values())

from django.db.models.functions import ExtractYear

def get_distinct_years():
    years = Order.objects.annotate(
        year=ExtractYear('order_date')
    ).values_list('year',flat=True).distinct()

    return list(years)


def SaleReport(request):
    if request.method == 'POST':
        try:
            year = int(request.POST.get('year'))
            data = get_orders_per_month(year)
            return JsonResponse({'success':True , 'dataset' : data})
        except:
            return JsonResponse({'success':False})
from django.utils import timezone

def get_today_sale():
    count = Order.objects.filter(order_date = timezone.now()).count()
    target = 50
    return {'target':target , 'sale' : count}

from datetime import datetime


@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def home(request):
    if not request.user.is_authenticated:
        return redirect('Ecom:login')
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('Ecom:home')
    current_year =datetime.now().year
    today_sale = get_today_sale()
    dataset = get_orders_per_month(current_year)
    years = get_distinct_years()
    return render(request , 'admin/home.html' ,{'dataset':dataset , 'years' : years , 'currentyear':current_year , 'today_sale':today_sale})


# def Users(request):
#     return render(request , "admin/users.html")
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserList(ListView):
    template_name = 'admin/users.html'
    context_object_name ='users'

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)
    
   
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')    
class UserDetail(DetailView):
    model = UserProfile 
    template_name="admin/userdetail.html"
    context_object_name = 'user'
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')  
@method_decorator(login_required, name='dispatch')
class ToggleUserActiveStatus(View):
    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('pk')
        try:
            user = User.objects.get(pk=id)
            user.is_active = not user.is_active
            user.save()
            return JsonResponse({'success': True, 'is_active': user.is_active})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'User not found'})
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')        
class CategoryList(ListView):
    model = Category
    template_name = 'admin/categorylist.html'
    context_object_name ='categorys'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the "modal" data to the context
        context['form'] = CategoryForm()  # Replace with your query

        return context

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')   
@method_decorator(login_required, name='dispatch')   
class CategoryDetail(DetailView):
    model = UserProfile 
    template_name="admin/categorydetail.html"
    context_object_name = 'category'
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')  
@method_decorator(login_required, name='dispatch')
class AddCategory(View):
    http_method_names=['post']
    def post(self, request, *args, **kwargs):
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            count  = Category.objects.aggregate(count = Count('id'))
            category_data = {
                'id': category.id,
                'name': category.name,
                'count':count['count']
            }
            
            return JsonResponse({'success': True, 'category_data': category_data})
        else:
            return JsonResponse({'success': False, 'error_message': 'Invalid form data'})

    
           
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')        
@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            self.object.delete()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': 'User not found'})
        
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')        
@method_decorator(login_required, name='dispatch')
class DeleteProduct(DeleteView):
    model = Product
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        try:
            self.object.active = False
            self.object.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': 'Product not found'})
        

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')        
@method_decorator(login_required, name='dispatch')
class UpdateProduct(UpdateView):

    model=Product

    template_name = 'admin/updateproduct2.html'

    context_object_name = 'product'

    form_class = UpdatedProductAddForm
    def get_success_url(self):
        return reverse('admins:productvarient',kwargs={'pk':self.kwargs['pk'] })


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProductList(ListView):
    model = Product
    template_name= 'admin/productlist.html'
    context_object_name ='products'

    def get_queryset(self):
        return Product.objects.filter(active = True)

class ProductVarient( CreateView ):
    model = Connector
    template_name = 'admin/productvarient.html'
    form_class = AddAditionVarientForm

    def dispatch(self, request, *args, **kwargs):
        product_id = self.kwargs['pk']
        if not Product.objects.filter(id=product_id).exists():
            return redirect('admins:productlist')
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        product_id = self.kwargs['pk']
        product = Product.objects.get(id=product_id)
        context['product'] = product
        context['varients'] = Connector.objects.filter(product=product)
        return context
    
    def form_invalid(self, form):
        context = self.get_context_data()
        context['error'] = 'invalid data'
        return self.render_to_response(context)
    
    def form_valid(self, form):
        form.save()
        return redirect('admins:productvarient' , pk=self.kwargs['pk'])
    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class ProductDetail(DetailView):
    model = Product
    template_name = "admin/productdetail.html"
    context_object_name = 'product'

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     context =  super().get_context_data(**kwargs)

    #     sizes = Connector.objects.filter(product = context['product'].product).filter(color =context['product'].color )

    #     context["sizes"] = sizes
    #     return context
    

def add_product(request):
    product_form = ProductForm()
    # size_count_formset = SizeCountForm(prefix='size_count')
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES)

        size_count_formse = formset_factory(SizeCountForm)
        size_count_formset = size_count_formse(request.POST)

        if product_form.is_valid() and size_count_formset.is_valid():
            # size_count_formset = product_form.cleaned_data['size_count_formset']
            # Create Product and ProductImage objects
            product = product_form.save(commit=False)
            product.brand = product_form.cleaned_data['brand']
            product.category = product_form.cleaned_data['category']
            product.save()

            normal_image = product_form.cleaned_data['normal_image']
            front_image = product_form.cleaned_data['front_image']
            back_image = product_form.cleaned_data['back_image']
            side_image = product_form.cleaned_data['side_image']

            product_image = ProductImage(normal_image=normal_image, front_image=front_image, back_image=back_image, side_image=side_image)
            product_image.save()

            color = product_form.cleaned_data['color']

            # Create Connector objects for each size and count
            for form in size_count_formset:
                size = form.cleaned_data.get('size')
                count = form.cleaned_data.get('count')

                connector = Connector(product=product, color=color, image=product_image, size=size, count=count)
                connector.save()

            return redirect('admins:productlist')  # Redirect to the product list page after successful creation


    return render(request, 'admin/addproduct.html', {'product_form': product_form})
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class AddProduct(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin/addproduct.html'


    def form_valid(self, form):
        size_count_formse = formset_factory(SizeCountForm)
        size_count_formset = size_count_formse(self.request.POST)
        if size_count_formset.is_valid():
            # print("helo")
            product = form.save(commit=False)
            product.brand = form.cleaned_data['brand']
            product.category = form.cleaned_data['category']
            
            product.save()

            normal_image = form.cleaned_data['normal_image']
            front_image = form.cleaned_data['front_image']
            back_image = form.cleaned_data['back_image']
            side_image = form.cleaned_data['side_image']

            product_image = ProductImage(normal_image=normal_image, front_image=front_image, back_image=back_image, side_image=side_image)
            product_image.save()

            

            color = form.cleaned_data['color']

            for size_count_form in size_count_formset:
                size = size_count_form.cleaned_data.get('size')
                count = size_count_form.cleaned_data.get('count')

                connector = Connector(product=product, color=color, image=product_image, size=size, count=count)
                if not Connector.objects.filter(product = product).exists():
                    connector.first_preference = True
                connector.save()

            return redirect('admins:productlist')
        return self.render_to_response(self.get_context_data(form=form))



@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def update_product(request,pk):
    if not request.user.is_authenticated:
        return redirect('Ecom:login')
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('Ecom:home')
    product = Connector.objects.get(pk=pk)
    forms = UpdateProductVarient(instance=product)

    if request.method == "POST":
        forms = UpdateProductVarient(request.POST , instance=product)
        if forms.is_valid():
            
            forms.save()
            # print("not entered")

            

            if request.FILES.get('normal_image'):
                product.image.normal_image = request.FILES['normal_image']
            if request.FILES.get('front_image'):
                product.image.front_image = request.FILES['front_image']
            if request.FILES.get('back_image'):
                product.image.back_image =request.FILES['back_image']
            if request.FILES.get('side_image'):
                product.image.side_image =request.FILES['side_image']
            product.image.save()
            product.save()
            return redirect('admins:productvarient' ,pk=product.product.id)


    return render(request,'admin/updateproduct.html',{'form' :forms,'product':product})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class OrderList(ListView):
    model = Order
    template_name= 'admin/orderlist.html'
    context_object_name ='orders'



    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class OrderDetail(DetailView):
    model = Order
    template_name= 'admin/orderdetail.html'
    context_object_name ='order'  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_instance = self.get_object()  # Get the instance of the Order model
        form = OredrFormStatus(instance=order_instance)  # Pass the instance to the form
        context['form'] = form
        return context
    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')   
class OrderUpdate(UpdateView):

    http_method_names = ['post']

    def post(self, *args, **kwargs):
        try:
            # print(self.request.PUT)
            order = Order.objects.get(id = kwargs.get('pk') )
            order.status = self.request.POST.get('status')
            if self.request.POST.get('status') == 'cancel':
                print('yes')
                for i in order.product_cover.all():
                    obj = i.products
                    obj.count += 1
                    obj.sale -= 1
                    obj.save()
                if UserWallet.objects.filter(user = order.user).exists():
                    wallet = UserWallet.objects.get(user = order.user)
                else:
                    wallet = UserWallet(user = order.user)
                wallet.balance = wallet.balance+ order.total_price
                wallet.save()
            order.save()
            return JsonResponse({'success': True , 'value':order.status})

        except order.DoesNotExist:
            return JsonResponse({'success': False})

def  CouponManager(request):
    coupon = form.CouponForm()
    if request.method == "POST":
        coupon = form.CouponForm(request.POST)
        if coupon.is_valid():
            coupon.save()
            messages.success(request, 'Coupon is added')
            return redirect('admins:coupon')
    all_coupon  = Coupon.objects.all()
    return render(request,'admin/coupon.html' , {'form':coupon , 'coupon' : all_coupon}) 


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')        
@method_decorator(login_required, name='dispatch')
class DeleteCoupon(DeleteView):
    model = Coupon
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):
        

        try:
            self.object = self.get_object()
            self.object.delete()
            return JsonResponse({'success':True})
        except Coupon.DoesNotExist:
            return JsonResponse({'success':False , 'error' : 'invalid coupon id'})

def UpdateCoupon(request , pk):
    obj = Coupon.objects.get(pk =pk)
    coupon = form.CouponForm(instance=obj)

    if request.method == 'POST':
        coupon = form.CouponForm(request.POST , instance=obj)
        if coupon.is_valid():
            coupon.save()
            messages.success(request, 'Coupon is updated')
            return redirect('admins:coupon')
        print(coupon.cleaned_data)
    return render(request,'admin/updatecoupon.html',{'form':coupon}) 

def logouts(request):

    logout(request)
    return redirect("admins:login")


class UpdatedAddProduct(CreateView):
    model = Product
    form_class = UpdatedProductAddForm
    template_name = 'admin/updatedaddproduct.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context.get('length'):
            
            context['varient_count_formset'] = VarientCountFormSetFactory(instance = self.request.POST or None , files = self.request.FILES or None , extra =context['length'] )
        else:
            context['varient_count_formset'] = VarientCountFormSetFactory(instance = self.request.POST or None ,files = self.request.FILES or None)
        a = 0
        for i in context['varient_count_formset']:
                
            i.size_count_formset =SizeCountFormSetFactory(instance = self.request.POST or None ,prefix = a)
            a  = a + 1 
        return context

    def form_valid(self, form):
        varient_formset = formset_factory(VarientForm , formset=VarientCountColorFormSet)
        each_varient_formset = varient_formset(self.request.POST,self.request.FILES , prefix='varient')
        
        if each_varient_formset.is_valid():
            each_size_form_count = 0
            for i in each_varient_formset:
                i.size_count_formset =SizeCountFormSetFactory(instance = self.request.POST or None ,prefix = each_size_form_count)
                if not i.size_count_formset.is_valid():
                    return self.render_to_response(self.get_context_data(form=form, length =len(each_varient_formset)))
                   
                each_size_form_count = each_size_form_count+1

            product = form.save()
            for value in each_varient_formset:

                normal_image = value.cleaned_data['normal_image']
                front_image = value.cleaned_data['front_image']
                back_image = value.cleaned_data['back_image']
                side_image = value.cleaned_data['side_image']

                product_image = ProductImage(normal_image=normal_image, front_image=front_image, back_image=back_image, side_image=side_image)
                product_image.save()
                color = value.cleaned_data['color']

                for size_count_form in value.size_count_formset:
                    size = size_count_form.cleaned_data.get('size')
                    count = size_count_form.cleaned_data.get('count')

                    if size:
                        connector = Connector(product=product, color=color, image=product_image, size=size, count=count)
                        if not Connector.objects.filter(product = product).exists():
                            connector.first_preference = True
                        connector.save()
            
            return redirect("admins:productlist")

        
        return self.render_to_response(self.get_context_data(form=form, length =len(each_varient_formset)))
    

def ProductVarientDelete(request , pk):
    if request.method == 'DELETE':
        
        try:
            varient = Connector.objects.get(id=pk)
            if Connector.objects.filter(product = varient.product).count() ==1:
                return JsonResponse({'success': True , 'element_count' : False , 'error_message':'you need atleast one varient for a product.'})
            varient.delete()    
            return JsonResponse({'success': True , 'element_count' : True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error_message': 'User not found'})

        

class AddAdditionProductVarient(CreateView):
    model=Connector
    template_name='admin/addadditionproductvarient.html'

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        form = super().get_form(form_class)
        form.size_count_formset = SizeCountFormSetFactory(instance=self.request.POST or None, prefix=0)
        product = Product.objects.get(pk = self.kwargs['pk'])
        form.initial['product'] = product
        return form
    
    def get_form_class(self):
        return AddAditionVarientColorForm

    def form_valid(self, form):
        
        form.size_count_formset = SizeCountFormSetFactory(instance=self.request.POST or None, prefix=0)
        if not form.size_count_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        
        image = ProductImage()
        image.front_image = form.cleaned_data['front_image']
        image.back_image = form.cleaned_data['back_image']
        image.side_image = form.cleaned_data['side_image']
        image.normal_image = form.cleaned_data['normal_image']

        image.save()

        color = form.cleaned_data['color']
        product = form.cleaned_data['product']

        for each_form in form.size_count_formset:
            size = each_form.cleaned_data.get('size')
            count = each_form.cleaned_data.get('count')
            if size:
                connector = Connector(product = product , color = color , size = size , image = image , count = count)
                connector.save()

        return redirect('admins:productvarient' , pk=self.kwargs['pk'])