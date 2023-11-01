# Generated by Django 4.2.5 on 2023-10-31 14:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0026_alter_connector_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ratting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(default=5)),
                ('comment', models.CharField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratting_product', to='adminpanel.product')),
            ],
        ),
    ]
