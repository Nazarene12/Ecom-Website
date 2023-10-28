from django.urls import path
from . import views

app_name = 'Ecom'

urlpatterns = [
    # path('' , TemplateView.as_view(template_name = "demo.html")),

    path ('' ,views.HomeTemplate.as_view() , name="home" ),

    path ('login', views.customLogin , name='login'),
    path('signup' , views.customSignup , name='signup'),
    path ('verify/<str:email>' , views.verifyEmail , name='verify'),
    path('forgot' , views.forgot , name='forgot'),
    path('resetpassword',views.resetpassword,name='resetpassword'),

    path('products' , views.ProductList.as_view() , name='products'),
    path('products/<int:pk>' , views.productDetail.as_view() , name='product_detail'),
    path('cart',views.CartList.as_view() , name='cart'),
    path('profile',views.Profile.as_view() , name='profile'),
    path('editprofile' , views.UserProfileUpdate , name='editprofile'),
    path('changepassword',views.UserChangePassword , name='changepassword'),
    path('addaddress',views.UserAddAdress , name='addaddress'),
    path('address/<int:pk>/update' , views.UpdateAdress.as_view() , name='addressupdate'),
    path('f_handlecart',views.FormHandlerCart , name='f_handlecart'),
    path('checkout',views.CheckOut , name='checkout'),
    path('ordersuccess/<int:pk>',views.SuccessPage , name='successpage'),
    path('userorder' , views.UserOrder.as_view() , name='userorder'),
    path('online_payment/<int:pk>' , views.OnlinePayment , name='online_payment'),
    path('paymenthandler/<int:pk>' , views.PaymentHandler , name='paymenthandler'),
    path('invoice/<int:pk>' , views.render_pdf_view , name="invoice"),
    path('addwallet' , views.AddWallet , name='addwallet'),
    path('getrazerpayid' , views.create_razerpay_order , name='getrazerpayid'),
    path ('razerpayformhandler' , views.RazerPaymentHandler , name="razerpayformhandler"),
    path('piperestart' , views.RestartPipe , name='piperestart'),

    #json url

    path('getdataproduct/<int:pk>',views.GetProductData.as_view() , name='get_data_product'),
    path('addcart',views.AddCart.as_view() , name='addcart'),
    path('updatecart',views.UpdateCart.as_view() , name='updatecart'),
    path('deletecart' ,views.DeleteCart.as_view() , name='deletecart'),
    path('setprimary/<int:pk>' , views.SetPrimary.as_view() , name='setprimary'),
    path('address/<int:pk>/delete',views.DeleteAddress.as_view() , name='deleteaddress'),
    path('order/<int:pk>/cancel',views.CancelOrder.as_view() , name='cancelorder'),
    path('order/<int:pk>/return' , views.ReturnOrder.as_view() , name='returnorder'),
    path('userlike',views.LikeProduct.as_view() , name='userlike'),
    path('coupon',views.CouponManager.as_view() , name='coupon'),
    path('profileimage' ,views.ProfileImage , name='profileimage'),

    path('logouts',views.logouts , name='logouts') ,
    
]