## carts/urls.py

from django.urls import path
from .views import CartView, AddToCartView, RemoveFromCartView, UpdateCartItemView, WishlistView, AddToWishlistView, RemoveFromWishlistView, AddBundleToCartView

app_name = 'carts'

urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),
    path('add-to-cart/<slug:slug>/', AddToCartView.as_view(), name='add_to_cart'),
    path('add-bundle/<slug:slug>/', AddBundleToCartView.as_view(), name='add_bundle'),
    path('remove-from-cart/<int:pk>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update-cart-item/<int:pk>/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('add-to-wishlist/<slug:slug>/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('remove-from-wishlist/<slug:slug>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
]