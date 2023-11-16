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
    path('export/', views.export_to_excel, name='export_to_excel'),
    path('exportpdf/', views.export_to_pdf, name='export_to_pdf'),
    path('stock',views.StockList.as_view() , name='stock'),


    path('color' , views.ColorList.as_view() , name='color'),
    path('color/add' , views.AddColor.as_view() , name='addcolor'),
    path('color/<int:pk>/delete' , views.DeleteColor.as_view() , name='deletecolor'),

    
    path('size' , views.SizeList.as_view() , name='size'),
    path('size/add' , views.AddSize.as_view() , name='addsize'),
    path('size/<int:pk>/delete' , views.DeleteSize.as_view() , name='deletesize'),


    path('brand' , views.BrandList.as_view() , name='brand'),
    path('brand/add' , views.AddBrand.as_view() , name='addbrand'),
    path('brand/<int:pk>/delete' , views.DeleteBrand.as_view() , name='deletebrand'),
    


    path('orders',views.OrderList.as_view() , name="order"),
    path('order/<int:pk>',views.OrderDetail.as_view() , name='orderdetail'),
    path('order/<int:pk>/update',views.OrderUpdate.as_view() , name='orderupdate'),


    path('offer' , views.Offer.as_view() , name='offer'),
    path('offer/product/<int:pk>' , views.OfferProduct , name='offerproduct'),
    path('offer/category/<int:pk>' , views.OfferCategory , name='offercategory'),
    

    path('coupon' , views.CouponManager , name = 'coupon'),
    path('coupon/<int:pk>/delete' , views.DeleteCoupon.as_view() , name='deletecoupon'),
    path('coupon/<int:pk>/update' , views.UpdateCoupon , name='updatecoupon'),

    path('salesreport' , views.SaleReport , name="salesreport"),

    path('logout',views.logouts , name='logout'),

]