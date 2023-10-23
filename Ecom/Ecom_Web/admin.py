from django.contrib import admin
from .models import UserProfile,Address,Order,UserCart
# Register your models here.


admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(UserCart)