# Generated by Django 4.2.5 on 2023-10-24 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecom_Web', '0002_remove_order_products_productordered'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product_cover',
            field=models.ManyToManyField(blank=True, default=None, related_name='product_cover', to='Ecom_Web.productordered'),
        ),
    ]