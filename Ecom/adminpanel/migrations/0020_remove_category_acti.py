# Generated by Django 4.2.5 on 2023-10-30 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0019_category_acti'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='acti',
        ),
    ]
