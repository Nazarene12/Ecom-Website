# Generated by Django 4.2.5 on 2023-10-24 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Ecom_Web', '0003_order_product_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='productordered',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
