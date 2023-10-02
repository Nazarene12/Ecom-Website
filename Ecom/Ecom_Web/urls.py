from django.urls import path
from django.views.generic import TemplateView

app_name = 'app1'

urlpatterns = [
    path('' , TemplateView.as_view(template_name = "demo.html")),
    
]