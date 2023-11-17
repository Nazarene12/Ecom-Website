from typing import Any
from django.db import models
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



from Ecom_Web import form
from.forms import CategoryForm,ProductForm,SizeCountForm,UpdateProductVarient,UpdatedProductAddForm,VarientForm,VarientCountFormSetFactory,SizeCountFormSetFactory,VarientCountColorFormSet,SizeCountFormSet, AddAditionVarientForm,AddAditionVarientColorForm,OredrFormStatus,ColorForm,SizeForm,BrandForm
from Ecom_Web.models import UserProfile,Order,Coupon,UserWallet
from .models import Category,Product,Connector,ProductImage,Color,Size,Brand,Transaction


from django.db.models import Count
from django.db.models.functions import TruncMonth
# Create your views here.

from django.contrib.auth.mixins import UserPassesTestMixin

from django.http import HttpResponse
from openpyxl import Workbook
from xhtml2pdf import pisa
from django.template.loader import get_template


def export_to_pdf(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    order = Order.objects.filter(order_date__gte = start,order_date__lte = end)
    template_path = 'admin/salesreport.html'
    context = {'orders': order}
   
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

def export_to_excel(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales report"

    # Add headers
    headers = ["order_id","order_date","products", "user" , "total_price" ,"total_item" ,"payment_method" ]
    ws.append(headers)

    # Add data from the model
    order = Order.objects.filter(order_date__gte = start,order_date__lte = end)
    for i in order:
        product=""
        for j in i.product_cover.all():
            product +=j.products.product.name

        ws.append([f"ORD{i.id}",str(i.order_date),product,i.user.username,i.total_price,i.total_item,i.payment_method])

    # Save the workbook to the HttpResponse
    wb.save(response)
    return response

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
from django.db.models import Sum  ,Count

def total_sales_year():
    sales = Order.objects.filter(order_date__year=timezone.now().year)
    
    # Calculate total sales amount and count of sales for the current day
    total_sales = sales.aggregate(total_sales_amount=Sum('total_price'), total_sales_count=Count('id'))
    
    # Accessing the total sales amount and count
    return total_sales
def total_sales_month():
    sales = Order.objects.filter(order_date__month=timezone.now().month)
    
    # Calculate total sales amount and count of sales for the current day
    total_sales = sales.aggregate(total_sales_amount=Sum('total_price'), total_sales_count=Count('id'))
    
    # Accessing the total sales amount and count
    return total_sales
def total_sales_today():
    sales = Order.objects.filter(order_date__date=timezone.now().date())
    
    # Calculate total sales amount and count of sales for the current day
    total_sales = sales.aggregate(total_sales_amount=Sum('total_price'), total_sales_count=Count('id'))
    
    # Accessing the total sales amount and count
    return total_sales



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
    total_sales_year_value = total_sales_year()
    total_sales_month_value = total_sales_month()
    total_sales_today_value = total_sales_today()
    return render(request , 'admin/home.html' ,{'dataset':dataset , 'years' : years , 'currentyear':current_year , 'today_sale':today_sale , 'total_sales_year_value':total_sales_year_value , 'total_sales_month_value':total_sales_month_value,'total_sales_today_value':total_sales_today_value})

class Offer(TemplateView):
    template_name = "admin/offer.html" 

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        search_parm = self.request.GET.get('search')
        offer_querset =  Product.objects.filter(category__active = True , brand__active = True)
        if search_parm:
            offer_querset = offer_querset.filter(name__icontains = search_parm)
        for each in offer_querset:

            each.varient  = each.detail_product.filter().first()

        context['offerproduct'] = offer_querset

        category = Category.objects.filter(active = True)
        context['category'] = category
        return context

def OfferProduct(request,pk):
    if request.method== 'POST':
        try:
            obj = Product.objects.get(pk =pk)
            discount = request.POST.get('discount')
            obj.discount = discount
            obj.price = obj.maximum_retail_price - (obj.maximum_retail_price* int(discount) /100)
            obj.save()
            return JsonResponse({'success':True , 'sale_price':obj.price})
        except:
            return JsonResponse({'success':False})
        
def OfferCategory(request,pk):
    if request.method== 'POST':
        try:
            print('g')
            category = Category.objects.get(id = pk)
            print(category)
            obj = Product.objects.filter(category =category )
            print(obj)
            discount = request.POST.get('discount')
            for i in obj:
                i.discount = discount
                i.price = i.maximum_retail_price - (i.maximum_retail_price* int(discount) /100)
                i.save()
            return JsonResponse({'success':True })
        except:
            return JsonResponse({'success':False})

@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class UserList(ListView):
    template_name = 'admin/users.html'
    context_object_name ='users'

    def get_queryset(self):
        search_term = self.request.GET.get('search')
        obj = User.objects.filter(is_superuser=False)
        if search_term:
            obj = obj.filter(user__first_name__icontains=search_term)
        return obj
    
from django.shortcuts import get_object_or_404 
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')    
class UserDetail(DetailView):
    model = UserProfile 
    template_name="admin/userdetail.html"
    context_object_name = 'user'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context =  super().get_context_data(**kwargs)
        user_profile = get_object_or_404(UserProfile, id=self.kwargs['pk'])
        context['transaction'] = Transaction.objects.filter(user = user_profile.user).order_by('-id')
        search_term = self.request.GET.get('search')
        obj = Order.objects.filter(user= user_profile.user).order_by('-id')
        if search_term:
            obj = obj.filter(product_cover__products__product__name__icontains=search_term)
       
        context['order'] = obj
        return context
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

    def get_queryset(self) -> QuerySet[Any]:
        return Category.objects.filter(active = True)


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
        

        try:
            self.object = self.get_object()
            self.object.active = False
            self.object.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': 'User not found'})
        

class ColorList(ListView) :
    model = Color
    template_name = 'admin/colorlist.html'
    context_object_name ='colors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the "modal" data to the context
        context['form'] = ColorForm()  # Replace with your query

        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return Color.objects.filter(active = True)
    
class AddColor(View):
    http_method_names=['post']
    def post(self, request, *args, **kwargs):
        form = ColorForm(request.POST)
        if form.is_valid():
            color = form.save()
            
            color_data = {
                'id': color.id,
                'name': color.name,
                'color':color.color
            }
            
            return JsonResponse({'success': True, 'color_data': color_data})
        else:
            errors = form.errors.as_json()
            if 'color' in form.errors:
                return JsonResponse({'success': False,'error':'color'})
            return JsonResponse({'success': False,'error':'name'})

class DeleteColor(DeleteView):
    model = Color
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):
        

        try:
            self.object = self.get_object()
            self.object.active = False
            self.object.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': 'color not found'})
        
class BrandList(ListView) :
    model = Brand
    template_name = 'admin/Brandlist.html'
    context_object_name ='brands'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the "modal" data to the context
        context['form'] = BrandForm()  # Replace with your query

        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return Brand.objects.filter(active = True)
    
class AddBrand(View):
    http_method_names=['post']
    def post(self, request, *args, **kwargs):
        form = BrandForm(request.POST , request.FILES)
        if form.is_valid():
            brand = form.save()
            
            brand_data = {
                'id': brand.id,
                'name': brand.name,
                'brand':brand.logo.url
            }
            
            return JsonResponse({'success': True, 'brand_data': brand_data})
        
            
        return JsonResponse({'success': False})

class DeleteBrand(DeleteView):
    model = Brand
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):
        

        try:
            self.object = self.get_object()
            self.object.active = False
            self.object.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': 'brand not found'})
        
class SizeList(ListView) :
    model = Size
    template_name = 'admin/sizelist.html'
    context_object_name ='sizes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the "modal" data to the context
        context['form'] = SizeForm()  # Replace with your query

        return context
    
    def get_queryset(self) -> QuerySet[Any]:
        return Size.objects.filter(active = True)
    
class AddSize(View):
    http_method_names=['post']
    def post(self, request, *args, **kwargs):
        form = SizeForm(request.POST)
        if form.is_valid():
            size = form.save()
            
            size_data = {
                'id': size.id,
                'size':size.size
            }
            
            return JsonResponse({'success': True, 'size_data': size_data})
        
        error_message = ''
        for field, errors in form.errors.items():
            if field == 'size':
                error_message += ' '.join(errors)
    
        return JsonResponse({'success': False , 'error' :error_message })

class DeleteSize(DeleteView):
    model = Size
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):        

        try:
            self.object = self.get_object()
            self.object.active = False
            self.object.save()
            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'error_message': 'size not found'})
           

        
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')        
@method_decorator(login_required, name='dispatch')
class DeleteProduct(DeleteView):
    model = Product
    http_method_names=['delete']

    def delete(self, request, *args, **kwargs):
        
        try:
            self.object = self.get_object()
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
    
@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class StockList(ListView):
    model = Connector
    template_name= 'admin/stocklist.html'
    context_object_name ='stocks'

    def get_queryset(self):
        search_term = self.request.GET.get('search')
        obj = Connector.objects.filter(active=True).order_by('count', '-sale')
        if search_term:
            obj = obj.filter(product__name__icontains=search_term)
        return obj

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
        context['varients'] = Connector.objects.filter(product=product , active = True)
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

            if request.GET.get('stock'):
                return redirect('admins:stock')
            return redirect('admins:productvarient' ,pk=product.product.id)


    return render(request,'admin/updateproduct.html',{'form' :forms,'product':product})


@method_decorator(cache_control(no_cache=True, must_revalidate=True, no_store=False), name='dispatch')
@method_decorator(login_required, name='dispatch')
class OrderList(ListView):
    model = Order
    template_name= 'admin/orderlist.html'
    context_object_name ='orders'
    paginate_by=10

    def get_queryset(self) -> QuerySet[Any]:
        search_term = self.request.GET.get('search')
        obj = Order.objects.all()
        if search_term:
            obj = obj.filter(product_cover__products__product__name__icontains=search_term)
        return obj



    
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
    search_param = request.GET.get('search')
    if request.method == "POST":
        coupon = form.CouponForm(request.POST)
        if coupon.is_valid():
            coupon.save()
            messages.success(request, 'Coupon is added')
            return redirect('admins:coupon')
    all_coupon  = Coupon.objects.all()
    if search_param:
        all_coupon = all_coupon.filter(coupon_code__icontains = search_param)
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
            if Connector.objects.filter(product = varient.product , active = True).count() ==1:
                return JsonResponse({'success': True , 'element_count' : False , 'error_message':'you need atleast one varient for a product.'})
            varient.active = False
            if varient.first_preference:
                
                other_varient = Connector.objects.filter(product=varient.product , active=True).exclude(id = varient.id).first()
                other_varient.first_preference=True
                
                other_varient.save()
            varient.first_preference = False
            varient.save()   
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


