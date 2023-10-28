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
    path('productlist', views.ProductList.as_view() , name='productlist'),
    path('product/<int:pk>/delete',views.DeleteProduct.as_view(), name='deleteproduct'),
    path('product/<int:pk>/update',views.UpdateProduct.as_view() , name='updateproduct2'),
    path('productvarient/<int:pk>' , views.ProductVarient.as_view() , name="productvarient"),
    path('productvarient/<int:pk>/delete', views.ProductVarientDelete, name='productvarientdelete'),
    path('productvarient/<int:pk>/add' , views.AddAdditionProductVarient.as_view() , name='addadditionalvarientproduct'),
    path('productdetail/<int:pk>', views.ProductDetail.as_view() , name='productdetail'),
    path('addproduct',views.UpdatedAddProduct.as_view() , name ='add_product'),
    path('updateproduct/<int:pk>',views.update_product , name='updateproduct'),

    path('orders',views.OrderList.as_view() , name="order"),
    path('order/<int:pk>',views.OrderDetail.as_view() , name='orderdetail'),
    path('order/<int:pk>/update',views.OrderUpdate.as_view() , name='orderupdate'),

    path('coupon' , views.CouponManager , name = 'coupon'),
    path('coupon/<int:pk>/delete' , views.DeleteCoupon.as_view() , name='deletecoupon'),
    path('coupon/<int:pk>/update' , views.UpdateCoupon , name='updatecoupon'),

    path('salesreport' , views.SaleReport , name="salesreport"),

    path('logout',views.logouts , name='logout'),

]