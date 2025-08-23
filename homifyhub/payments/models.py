from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from orders.models import Order  # Assuming orders app
from core.utils import imgbb_upload  # For proof upload

class Payment(models.Model):
    """
    Model for payments. Linked to an Order (one-to-one).
    - order: OneToOneField to Order.
    - from_account: Account number/string.
    - method: Choice (bKash, Nagad, Stripe, Bank Transfer).
    - amount: Float (matches order.total_amount).
    - transaction_id: String ID.
    - note: Optional text.
    - status: Choice (Pending, Completed, Failed, Refunded, Partially Refunded, Cancelled).
    - is_confirmed: Boolean (seller approval).
    - proof_url: URL to uploaded proof (imgbb).
    - created_at: Timestamp.
    - updated_at: Timestamp.
    Seller approves in admin, triggers order update.
    Users upload proof optionally.
    """
    METHOD_CHOICES = (
        ('bKash', 'bKash'),
        ('Nagad', 'Nagad'),
        ('Stripe', 'Stripe'),
        ('Bank Transfer', 'Bank Transfer'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
        ('Partially Refunded', 'Partially Refunded'),
        ('Cancelled', 'Cancelled'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment', verbose_name=_("Order"))
    from_account = models.CharField(max_length=50, verbose_name=_("From Account"))
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name=_("Payment Method"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Amount"))
    transaction_id = models.CharField(max_length=100, verbose_name=_("Transaction ID"))
    note = models.TextField(blank=True, verbose_name=_("Note"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name=_("Status"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Is Confirmed"))
    proof_url = models.URLField(blank=True, null=True, verbose_name=_("Proof URL"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment for Order {self.order.order_number}"

    def save(self, *args, **kwargs):
        if self.amount != self.order.total_amount:
            raise ValueError("Payment amount must match order total.")
        super().save(*args, **kwargs)