
from django.db import models
from django.contrib.auth.models import User
from adminpanel.models import Product , Connector
from django.core.validators import MaxValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE , related_name="user")
    first_name = models.CharField(max_length=30, blank=False , null=False  , help_text='required*')
    last_name = models.CharField(max_length=30 ,blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField( blank=False , null=False , help_text='required*')
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], blank=False , null=False  ,default='male')
    picture = models.ImageField(upload_to="profile/", blank=True, null=True)
    # Add other fields as needed for your user profile

    def __str__(self):
        return self.user.username

class UserCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='user_detail')
    connect = models.ForeignKey(Connector, on_delete=models.CASCADE , related_name='connect')
    quantity = models.IntegerField(blank=False , null=False , default=1)
    delete_cart = models.BooleanField(default=False)

    def __str__(self):
        return self.connect.product.name

    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    village = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    landmark = models.CharField(max_length=200 , blank=True , null=True)
    first_phone_number = models.CharField(max_length=15)
    second_phone_number = models.CharField(max_length=15, blank=True, null=True)
    primary_address = models.BooleanField(blank=True, null=True , default=False)
    delete_address = models.BooleanField(default=False)

    def __str__(self):
        return f' {self.village}, {self.city} , {self.district} - {self.pincode} ,{self.first_phone_number}'


def get_delivery_date():
    return timezone.now() + timezone.timedelta(days=7)


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('cancel', 'Canceled'),
        ('delivered', 'Delivered'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('online', 'Online Payment'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )

    order_date = models.DateTimeField(default=timezone.now)
    delivery_date = models.DateTimeField(default=get_delivery_date)
    products = models.ManyToManyField(Connector,related_name='order_product')
    user = models.ForeignKey(User, on_delete=models.CASCADE , related_name='order_user')
    address = models.ForeignKey(Address, on_delete=models.CASCADE , related_name='order_user_address')
    total_price = models.CharField(max_length=10)
    total_item = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'Order #{self.pk}'
    
class CancelOrder(models.Model):
    COLOR_CHOICES = [
        ('NM', 'Color not match'),
        ('WS', 'Wrong size'),
        ('QG', 'Quality not good'),
    ]

    orderid = models.ForeignKey(Order, on_delete=models.CASCADE)
    choice = models.CharField(max_length=2, choices=COLOR_CHOICES)
    text = models.TextField()

    def __str__(self):
        return f"Order {self.pk}"