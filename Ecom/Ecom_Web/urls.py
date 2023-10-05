from django.urls import path
from . import views

app_name = 'app1'

urlpatterns = [
    # path('' , TemplateView.as_view(template_name = "demo.html")),

    path ('' ,views.HomeTemplate.as_view() , name="home" ),

    path ('login', views.customLogin , name='login'),
    path('signup' , views.customSignup , name='signup'),
    path ('verify/<str:email>' , views.verifyEmail , name='verify')
    
]