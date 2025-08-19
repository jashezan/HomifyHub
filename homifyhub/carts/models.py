## carts/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product, Variant, Bundle
from django.core.exceptions import ValidationError

User = get_user_model()


class Cart(models.Model):
    """
    Model for user carts. One per user.
    - user: OneToOneField to User.
    - created_at: Timestamp.
    - updated_at: Timestamp.
    Items via CartItem.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart", verbose_name=_("User")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")

    def __str__(self):
        return f"Cart for {self.user}"

    @property
    def total(self):
        """Total cart value."""
        items = getattr(self, "items", None)
        if items is None:
            from .models import CartItem

            items = CartItem.objects.filter(cart=self)
        return sum(item.subtotal for item in items.all())

    @property
    def item_count(self):
        """Total items in cart."""
        items = getattr(self, "items", None)
        if items is None:
            from .models import CartItem

            items = CartItem.objects.filter(cart=self)
        return items.count()


class CartItem(models.Model):
    """
    Model for items in cart.
    - cart: ForeignKey to Cart.
    - variant: Optional ForeignKey to Variant.
    - bundle: Optional ForeignKey to Bundle.
    - quantity: Positive integer.
    - customization: JSON for custom options.
    Ensure either variant or bundle, not both.
    """

    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name=_("Cart")
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Variant"),
    )
    bundle = models.ForeignKey(
        Bundle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Bundle"),
    )
    quantity = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)], verbose_name=_("Quantity")
    )
    customization = models.JSONField(
        default=dict, blank=True, verbose_name=_("Customization")
    )

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        unique_together = ("cart", "variant", "bundle")  # Prevent duplicates

    def __str__(self):
        item_name = (
            getattr(self.variant, "name", None)
            if self.variant
            else getattr(self.bundle, "name", "Unknown Item")
        )
        if item_name is None:
            item_name = (
                getattr(self.bundle, "name", "Unknown Item")
                if self.bundle
                else "Unknown Item"
            )
        return f"{item_name} (x{self.quantity}) in {self.cart}"

    @property
    def subtotal(self):
        price = 0
        if self.variant:
            price = getattr(self.variant, "final_price", 0)
        elif self.bundle:
            price = getattr(self.bundle, "final_price", 0)
        return price * self.quantity

    def clean(self):
        if not self.variant and not self.bundle:
            raise ValidationError("Must have either variant or bundle.")
        if self.variant and self.bundle:
            raise ValidationError("Cannot have both variant and bundle.")


class Wishlist(models.Model):
    """
    Model for user wishlist. M2M with Product.
    - user: ForeignKey to User.
    - products: M2M with Product.
    - created_at: Timestamp.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="wishlist", verbose_name=_("User")
    )
    products = models.ManyToManyField(
        Product, related_name="wishlisted_by", blank=True, verbose_name=_("Products")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

    def __str__(self):
        return f"Wishlist for {self.user}"
