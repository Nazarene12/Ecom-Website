from django.urls import path
from . import views

app_name = 'app1'

urlpatterns = [
    # path('' , TemplateView.as_view(template_name = "demo.html")),

    path ('' ,views.HomeTemplate.as_view() , name="home" ),

    path ('login', views.customLogin , name='login'),
    path('signup' , views.customSignup , name='signup'),
    path ('verify/<str:email>' , views.verifyEmail , name='verify'),
    path('forgot' , views.forgot , name='forgot'),
    path('resetpassword',views.resetpassword,name='resetpassword'),

    path('products' , views.ProductList.as_view() , name='products'),
    path('product_filter' , views.productFilter , name='product_filter'),
    path('products/<int:pk>' , views.productDetail.as_view() , name='product_detail'),

    #json url

    path('getdataproduct/<int:pk>',views.GetProductData.as_view() , name='get_data_product'),
    

    path('logouts',views.logouts , name='logouts') ,
    
]