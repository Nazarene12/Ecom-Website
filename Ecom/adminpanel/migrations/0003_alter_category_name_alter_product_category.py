# Generated by Django 4.2.5 on 2023-10-13 10:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0002_alter_category_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(default='hi', max_length=255, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(help_text='required*', null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminpanel.category'),
        ),
    ]