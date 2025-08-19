## carts/admin.py

from django.contrib import admin
from .models import Cart, CartItem, Wishlist

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin for Cart.
    """
    list_display = ('user', 'item_count', 'total', 'updated_at')
    search_fields = ('user__username',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """
    Admin for CartItem.
    """
    list_display = ('cart', 'variant', 'bundle', 'quantity', 'subtotal')
    list_filter = ('cart__user',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """
    Admin for Wishlist.
    """
    list_display = ('user', 'created_at')
    filter_horizontal = ('products',)