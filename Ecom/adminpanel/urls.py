from django.urls import path
from . import views

app_name = "admins"

urlpatterns = [
    path('login' , views.AdminLogin , name = 'login' ),
    path('home' , views.home , name = 'home' ),
    path('user' , views.UserList.as_view() , name='users' ),
    path('userdetail/<int:pk>' , views.UserDetail.as_view() , name='userdetail'),
    path("toggle_user_status/<int:pk>" , views.ToggleUserActiveStatus.as_view() , name='toggle_user_status'),
    path('category' , views.CategoryList.as_view() , name='category' ),
    path('category/<int:pk>' , views.CategoryDetail.as_view() , name='categorydetail'),
    path("category/<int:pk>/delete" , views.CategoryDeleteView.as_view() , name='delete_category'),
    path('addcategory' , views.AddCategory.as_view(), name='add_category'),

]