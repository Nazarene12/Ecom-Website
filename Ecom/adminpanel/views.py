from django.shortcuts import render
from django.shortcuts import render,redirect,HttpResponse
from django.views.generic.base import TemplateView
from django.views import View
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core import signing 
from django.urls import reverse
from django.contrib.auth import authenticate , login
from django.contrib import messages
from django.views.generic import ListView , DetailView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView
from django.views.decorators.http import require_http_methods

from django.db.models import Count



from Ecom_Web import form
from.forms import CategoryForm
from Ecom_Web.models import UserProfile
from .models import Category,Product

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def AdminLogin(request):
    if request.user.is_authenticated and not request.user.is_superuser:
        return redirect('Ecom:home')
    if request.user.is_authenticated and request.user.is_superuser:
        pass

    loginform = form.LoginForm(request.POST or None , request = request , log="admin")
    if request.POST.get('signin') and loginform.is_valid():
        messages.add_message(request,messages.SUCCESS, f'login sucess {loginform.cleaned_data.get("username")}',extra_tags="Login")
        return redirect('admins:home')

    return render (request , 'admin/login.html', {'form':loginform})


def home(request):
    return render(request , 'admin/home.html')


# def Users(request):
#     return render(request , "admin/users.html")

class UserList(ListView):
    template_name = 'admin/users.html'
    context_object_name ='users'

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)
   

    
class UserDetail(DetailView):
    model = UserProfile 
    template_name="admin/userdetail.html"
    context_object_name = 'user'
   

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
        
class CategoryList(ListView):
    model = Category
    template_name = 'admin/categorylist.html'
    context_object_name ='categorys'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add the "modal" data to the context
        context['form'] = CategoryForm()  # Replace with your query

        return context

    
    
class CategoryDetail(DetailView):
    model = UserProfile 
    template_name="admin/categorydetail.html"
    context_object_name = 'category'
   
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


