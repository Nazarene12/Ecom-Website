from django.contrib import admin

from .models import Category , Brand ,Color,Connector,Product,ProductImage,Size

# Register your models here.


admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(ProductImage)
admin.site.register(Size)
admin.site.register(Connector)