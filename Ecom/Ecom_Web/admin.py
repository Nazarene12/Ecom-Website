from django.contrib import admin
from .models import UserProfile,Address,Order,UserCart,ProductOrdered,Coupon,CancelOrder,UserWallet,UserWishList
# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(UserCart)
admin.site.register(Coupon)
admin.site.register(CancelOrder)
admin.site.register(UserWallet)
admin.site.register(UserWishList)
admin.site.register(ProductOrdered)
