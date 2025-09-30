from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from carts.models import Cart, Wishlist


@receiver(post_save, sender=User)
def create_user_cart_wishlist(sender, instance, created, **kwargs):
    if created:
        Cart.objects.get_or_create(user=instance)
        Wishlist.objects.get_or_create(user=instance)
