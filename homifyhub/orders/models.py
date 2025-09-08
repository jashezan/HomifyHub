from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from products.models import Product, Variant, Stock, Bundle
from users.models import Address  # Assuming Address model in users app
from site_settings.models import DeliveryMethod, Coupon  # Assuming these exist
from django_bleach.models import BleachField

User = get_user_model()


class Order(models.Model):
    """
    Model for orders. Represents a user's purchase.
    - user: ForeignKey to User (required).
    - order_number: Unique identifier (auto-generated).
    - status: Order status (e.g., Pending, Processing, Shipped, Delivered, Cancelled).
    - delivery_method: Chosen delivery method.
    - delivery_address: Shipping address (linked to Address model).
    - billing_address: Billing address (can differ from delivery).
    - coupon: Optional coupon applied.
    - total_amount: Total order value (after discounts).
    - created_at: Order creation timestamp.
    - updated_at: Last update timestamp.
    - notes: Optional user notes.
    Users can view history, track, or cancel (if payment not approved).
    Seller manages via admin.
    """

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", verbose_name=_("User")
    )
    order_number = models.CharField(
        max_length=20, unique=True, editable=False, verbose_name=_("Order Number")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
        verbose_name=_("Status"),
    )
    delivery_method = models.ForeignKey(
        "site_settings.DeliveryMethod", null=True, blank=True, on_delete=models.SET_NULL
    )
    delivery_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name="delivery_orders",
        verbose_name=_("Delivery Address"),
    )
    billing_address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name="billing_orders",
        verbose_name=_("Billing Address"),
    )
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Coupon"),
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Total Amount"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    notes = BleachField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order {self.order_number} by {self.user}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order_number, e.g., ORD-YYYYMMDD-XXXX
            from datetime import datetime

            date_str = datetime.now().strftime("%Y%m%d")
            last_order = (
                Order.objects.filter(order_number__startswith=f"ORD-{date_str}")
                .order_by("-order_number")
                .first()
            )
            if last_order:
                last_num = int(last_order.order_number.split("-")[-1]) + 1
            else:
                last_num = 1
            self.order_number = f"ORD-{date_str}-{last_num:04d}"
        super().save(*args, **kwargs)

    @property
    def is_cancellable(self):
        """Check if order can be cancelled (payment not approved)."""
        # Check if payment exists and is still pending
        try:
            payment = getattr(self, "payment", None)
            if payment:
                return payment.status in ["Pending"]
            return True  # If no payment exists, order can be cancelled
        except:
            return True


class OrderItem(models.Model):
    """
    Model for items in an order. Can be a product variant or bundle.
    - order: ForeignKey to Order.
    - variant: Optional ForeignKey to Variant (for products).
    - bundle: Optional ForeignKey to Bundle.
    - quantity: Number of units.
    - price_at_purchase: Price at time of purchase (handles price changes).
    - customization: JSON dict for customizations (e.g., {"color": "red"}).
    Links to OrderItemStock for stock tracking.
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", verbose_name=_("Order")
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Variant"),
    )
    bundle = models.ForeignKey(
        Bundle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Bundle"),
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Price at Purchase"),
    )
    customization = models.JSONField(
        default=dict, blank=True, verbose_name=_("Customization")
    )

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")

    def __str__(self):
        if self.variant:
            item_name = self.variant.name
        elif self.bundle:
            item_name = self.bundle.name
        else:
            item_name = "Unknown Item"
        return f"{item_name} (x{self.quantity}) in Order {self.order.order_number}"

    @property
    def subtotal(self):
        return self.price_at_purchase * self.quantity


class OrderItemStock(models.Model):
    """
    Tracks which stock was used for an order item (for FIFO accounting).
    - order_item: ForeignKey to OrderItem.
    - stock: ForeignKey to Stock.
    - quantity: Quantity taken from this stock.
    Updated via signals when order is placed.
    """

    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.CASCADE,
        related_name="stock_entries",
        verbose_name=_("Order Item"),
    )
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        related_name="order_entries",
        verbose_name=_("Stock"),
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))

    class Meta:
        verbose_name = _("Order Item Stock")
        verbose_name_plural = _("Order Item Stocks")

    def __str__(self):
        return f"{self.quantity} units from {self.stock} for {self.order_item}"


class DeliveryTracking(models.Model):
    """
    Model for real-time delivery tracking.
    - order: One-to-one with Order.
    - status: Current delivery status.
    - tracking_number: Courier tracking ID.
    - courier: Name of courier service.
    - estimated_delivery: Estimated delivery date.
    - updates: JSON field for status updates (e.g., [{"date": "", "status": ""}]).
    Seller updates via admin; users view in order tracking page.
    """

    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("In Transit", "In Transit"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
        ("Failed", "Failed"),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="tracking",
        verbose_name=_("Order"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
        verbose_name=_("Delivery Status"),
    )
    tracking_number = models.CharField(
        max_length=50, blank=True, verbose_name=_("Tracking Number")
    )
    courier = models.CharField(max_length=100, blank=True, verbose_name=_("Courier"))
    estimated_delivery = models.DateField(
        null=True, blank=True, verbose_name=_("Estimated Delivery")
    )
    updates = models.JSONField(
        default=list, blank=True, verbose_name=_("Status Updates")
    )

    class Meta:
        verbose_name = _("Delivery Tracking")
        verbose_name_plural = _("Delivery Trackings")

    def __str__(self):
        return f"Tracking for Order {self.order.order_number}"
