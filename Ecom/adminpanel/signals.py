from django.db.models.signals import post_delete,pre_delete,pre_save,post_save
from django.dispatch import receiver
from .models import Connector , ProductImage,Product,Brand


@receiver(pre_save, sender=Connector)
def delete_product_if_count_zero(sender, instance, **kwargs):
    if instance.count == 0:
        # instance.active = False
        pass

@receiver(pre_delete, sender=Connector)
def delete_product_media_if_one_connector_deleted(sender, instance, **kwargs):
    if not Connector.objects.filter(product = instance.product).filter(color =instance.color).exists() :
        instance.image.delete()

@receiver(pre_delete, sender=Brand)
def delete_product_media_if_one_connector_deleted(sender, instance, **kwargs):
    
    instance.logo.delete()

@receiver(post_save, sender=ProductImage)
def delete_old_images(sender, instance, **kwargs):
    if instance.pk is not None:
        instance.refresh_from_db()
        old_instance = ProductImage.objects.get(pk=instance.pk)
        if old_instance.front_image != instance.front_image:
            old_instance.front_image.delete()
        if old_instance.back_image != instance.back_image:
            old_instance.back_image.delete()
        if old_instance.side_image != instance.side_image:
            old_instance.side_image.delete()
        if old_instance.normal_image != instance.normal_image:
            old_instance.normal_image.delete()

@receiver(pre_delete, sender=ProductImage)
def delete_images(sender, instance, **kwargs):
    instance.front_image.delete()
    instance.back_image.delete()
    instance.side_image.delete()
    instance.normal_image.delete()

    