from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Connector


@receiver(post_delete, sender=Connector)
def delete_product_if_count_zero(sender, instance, **kwargs):
    if instance.count == 0:
        instance.product.delete()