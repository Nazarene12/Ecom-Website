from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from django.contrib.auth.models import User


# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)
    logo = models.ImageField(upload_to='brand/', blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=255,  blank=False, null=False)
    active = models.BooleanField(default=True)
    offer = models.IntegerField(  blank=True, default=0, null=True)

    def __str__(self):
        return self.name
    
    
    
class ProductImage(models.Model):
    front_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    back_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    side_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    normal_image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return f"ProductImage #{self.pk}"
    
class Size(models.Model):
    size = models.IntegerField(help_text='required*')
    active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.size)
    
    


class Color(models.Model):
    name = models.CharField(max_length=255,  blank=False , help_text='required*')
    color = models.CharField(max_length=255,  blank=False , help_text='required*')
    active = models.BooleanField(default=True)

      

    def __str__(self):
        return self.name
    

    
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False , help_text='required*')
    description = models.TextField(blank=False, null=False, help_text='required*')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False, help_text='required*')
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE,blank=False,null=False, help_text='required*')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,help_text='required*' , null=True)  # Default to 'normal' category
    maximum_retail_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, default=0.0, null=False, help_text='required*')
    discount = models.IntegerField(  blank=True, default=0, null=True,help_text='optional')
    offer = models.IntegerField(  blank=True, default=0, null=True)
    active = models.BooleanField(default=True)
    rating = models.IntegerField(default=5)
    

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.detail_product.all().delete()
        super().delete(*args, **kwargs)
    
class Connector(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='detail_product')
    color = models.ForeignKey(Color, on_delete=models.CASCADE,related_name='detail_color')
    image = models.ForeignKey(ProductImage, on_delete=models.CASCADE,related_name='detail_image')
    size = models.ForeignKey(Size,on_delete=models.CASCADE,related_name='detail_size')
    count = models.IntegerField(blank=False,null=False ,default=0)
    first_preference = models.BooleanField(default=False)
    sale = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    


    def __str__(self):
        return self.product.name

class Ratting(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='ratting_product')
    rating = models.IntegerField(default=5)


class Comment(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='comment_product')
    comment = models.CharField(max_length=100 , blank=False, null=False)

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.date} - Amount: {self.amount}"


