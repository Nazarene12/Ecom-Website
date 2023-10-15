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
from django.urls import reverse
from django.contrib.auth import authenticate , login ,logout
from django.contrib import messages
from django.views.generic import ListView , DetailView ,CreateView
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
from.forms import CategoryForm,ProductForm,SizeCountForm,UpdateProductVarient,UpdatedProductAddForm,VarientForm,VarientCountFormSetFactory,SizeCountFormSetFactory,VarientCountColorFormSet,SizeCountFormSet, AddAditionVarientForm,AddAditionVarientColorForm
from Ecom_Web.models import UserProfile
from .models import Category,Product,Connector,ProductImage

# Create your views here.

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

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def home(request):
    if not request.user.is_authenticated:
        return redirect('Ecom:login')
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('Ecom:home')
    return render(request , 'admin/home.html')


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
class ProductList(ListView):
    model = Product
    template_name= 'admin/productlist.html'
    context_object_name ='products'


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
            print("error")
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