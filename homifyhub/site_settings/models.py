from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django_bleach.models import BleachField


class SiteSettings(models.Model):
    """
    Singleton model for site-wide settings.
    - site_name: Name of the platform.
    - low_stock_threshold: Threshold for low stock warnings.
    - contact_email: Support email.
    - contact_phone: Support phone.
    - default_currency: Currency for pricing (e.g., USD).
    Only one instance should exist.
    """

    site_name = models.CharField(
        max_length=100, default="HomifyHub", verbose_name=_("Site Name")
    )
    low_stock_threshold = models.PositiveIntegerField(
        default=10, verbose_name=_("Low Stock Threshold")
    )
    contact_email = models.EmailField(verbose_name=_("Contact Email"))
    contact_phone = models.CharField(max_length=15, verbose_name=_("Contact Phone"))
    default_currency = models.CharField(
        max_length=3, default="USD", verbose_name=_("Default Currency")
    )

    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")

    def __str__(self):
        return "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class DeliveryMethod(models.Model):
    """
    Model for delivery methods.
    - name: Delivery method name (e.g., Standard Shipping).
    - cost: Delivery cost.
    - estimated_days: Estimated delivery time (days).
    - is_active: Whether available for selection.
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Cost"),
    )
    estimated_days = models.PositiveIntegerField(verbose_name=_("Estimated Days"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Delivery Method")
        verbose_name_plural = _("Delivery Methods")

    def __str__(self):
        return self.name


class Coupon(models.Model):
    """
    Model for discount coupons.
    - code: Unique coupon code.
    - discount_amount: Fixed discount amount.
    - is_active: Whether coupon is active.
    - valid_from, valid_until: Validity period.
    """

    code = models.CharField(max_length=20, unique=True, verbose_name=_("Code"))
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Discount Amount"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    valid_from = models.DateTimeField(verbose_name=_("Valid From"))
    valid_until = models.DateTimeField(verbose_name=_("Valid Until"))

    class Meta:
        verbose_name = _("Coupon")
        verbose_name_plural = _("Coupons")

    def __str__(self):
        return f"{self.code} (-${self.discount_amount})"


class PaymentMethod(models.Model):
    """
    Model for payment methods (seller bank info).
    - name: Payment method name (e.g., bKash, Bank Transfer).
    - details: Instructions or account details (sanitized).
    - is_active: Whether available for selection.
    """

    name = models.CharField(max_length=100, verbose_name=_("Name"))
    details = BleachField(verbose_name=_("Details"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Payment Method")
        verbose_name_plural = _("Payment Methods")

    def __str__(self):
        return self.name


class Banner(models.Model):
    """
    Model for homepage banners with auto-slider functionality.
    """

    title = models.CharField(max_length=200, verbose_name=_("Title"))
    subtitle = models.CharField(max_length=300, blank=True, verbose_name=_("Subtitle"))
    image_url = models.URLField(verbose_name=_("Image URL"))
    button_text = models.CharField(
        max_length=50, blank=True, verbose_name=_("Button Text")
    )
    button_link = models.URLField(blank=True, verbose_name=_("Button Link"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Banner")
        verbose_name_plural = _("Banners")
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title


class TopNotification(models.Model):
    """
    Model for top notification bar (closable).
    """

    message = models.CharField(max_length=300, verbose_name=_("Message"))
    background_color = models.CharField(
        max_length=7,
        default="#ff6b6b",
        help_text="Hex color code",
        verbose_name=_("Background Color"),
    )
    text_color = models.CharField(
        max_length=7,
        default="#ffffff",
        help_text="Hex color code",
        verbose_name=_("Text Color"),
    )
    link_url = models.URLField(blank=True, verbose_name=_("Link URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Top Notification")
        verbose_name_plural = _("Top Notifications")
        ordering = ["-created_at"]

    def __str__(self):
        return self.message[:50]


class FooterLink(models.Model):
    """
    Model for footer links organized by sections.
    """

    SECTION_CHOICES = [
        ("company", _("Company")),
        ("support", _("Support")),
        ("legal", _("Legal")),
        ("social", _("Social")),
    ]

    section = models.CharField(
        max_length=20, choices=SECTION_CHOICES, verbose_name=_("Section")
    )
    title = models.CharField(max_length=100, verbose_name=_("Title"))
    url = models.URLField(verbose_name=_("URL"))
    is_external = models.BooleanField(default=False, verbose_name=_("Is External Link"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    class Meta:
        verbose_name = _("Footer Link")
        verbose_name_plural = _("Footer Links")
        ordering = ["section", "order"]

    def __str__(self):
        return f"{self.get_section_display()} - {self.title}"


class ContactInfo(models.Model):
    """
    Model for contact information displayed in footer.
    """

    address = models.TextField(verbose_name=_("Address"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    email = models.EmailField(verbose_name=_("Email"))
    working_hours = models.CharField(max_length=100, verbose_name=_("Working Hours"))
    facebook_url = models.URLField(blank=True, verbose_name=_("Facebook URL"))
    twitter_url = models.URLField(blank=True, verbose_name=_("Twitter URL"))
    instagram_url = models.URLField(blank=True, verbose_name=_("Instagram URL"))
    linkedin_url = models.URLField(blank=True, verbose_name=_("LinkedIn URL"))

    class Meta:
        verbose_name = _("Contact Information")
        verbose_name_plural = _("Contact Information")

    def save(self, *args, **kwargs):
        self.pk = 1  # Ensure singleton
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Contact Information"
