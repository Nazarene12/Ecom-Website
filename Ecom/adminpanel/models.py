from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.


class Brand(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    logo = models.ImageField(upload_to='brand/', blank=True, null=True)

    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name
    
    def clean(self):
        # Custom validation logic to check for uniqueness
        existing_category = Category.objects.filter(name=self.name).exclude(pk=self.pk)
        if existing_category.exists():
            raise ValidationError("A category with this name already exists.")
    
class ProductImage(models.Model):
    front_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    back_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    side_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    normal_image = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return f"ProductImage #{self.pk}"
    
class Size(models.Model):
    size = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.size)


class Color(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=255, unique=True, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default=1)  # Default to 'normal' category

    def __str__(self):
        return self.name
    
class Connector(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='detail_product')
    color = models.ForeignKey(Color, on_delete=models.CASCADE,related_name='detail_color')
    image = models.ForeignKey(ProductImage, on_delete=models.CASCADE,related_name='detail_image')
    size = models.ForeignKey(Size,on_delete=models.CASCADE,related_name='detail_size')
    count = models.IntegerField()
    first_preference = models.BooleanField(default=False)
    sale = models.IntegerField(default=0)

    def __str__(self):
        return self.product.name
