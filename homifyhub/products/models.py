from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_bleach.models import BleachField  # For safe HTML in descriptions

User = get_user_model()

class Category(models.Model):
    """
    Model for product categories. Supports hierarchical categories (subcategories) via self-referential ForeignKey.
    - name: Human-readable name (e.g., "Furniture").
    - slug: URL-friendly slug, auto-generated.
    - parent: Optional parent category for subcategories.
    - description: Optional description for SEO and display.
    Used in product browsing, related products, and filtering.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories', verbose_name=_("Parent Category"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_full_path(self):
        """Returns the full category path for breadcrumbs, e.g., 'Home > Furniture > Sofas'."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))

class Tag(models.Model):
    """
    Model for product tags. Used for better searchability and related products.
    - name: Tag name (e.g., "modern", "eco-friendly").
    - slug: Auto-generated slug for URLs.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Main model for products. Represents a home decor item.
    - name: Product name.
    - slug: Auto-generated for URLs.
    - description: Detailed description (HTML-safe via BleachField).
    - categories: Many-to-many with Category.
    - tags: Many-to-many with Tag.
    - youtube_video_url: Optional YouTube URL for embedding in detail page.
    - specifications: JSON dict of specs (e.g., {"dimensions": "10x20", "material": "wood"}).
    - is_customizable: If true, show customization options in cart/add form.
    - customization_options: JSON dict (e.g., {"colors": ["red", "blue"], "engraving": true}).
    Managed by superuser via admin. Users browse via views/templates.
    Note: Price/discount/stock handled via Variant (always at least one variant per product).
    """
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = BleachField(verbose_name=_("Description"))  # Safe HTML
    categories = models.ManyToManyField(Category, related_name='products', blank=True, verbose_name=_("Categories"))
    tags = models.ManyToManyField(Tag, related_name='products', blank=True, verbose_name=_("Tags"))
    youtube_video_url = models.URLField(blank=True, null=True, verbose_name=_("YouTube Video URL"))
    specifications = models.JSONField(default=dict, blank=True, verbose_name=_("Specifications"))  # e.g., {"weight": "5kg", "material": "wood"}
    is_customizable = models.BooleanField(default=False, verbose_name=_("Is Customizable"))
    customization_options = models.JSONField(default=dict, blank=True, verbose_name=_("Customization Options"))  # e.g., {"sizes": ["S", "M"], "colors": ["red"]}

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def primary_image(self):
        """Returns the primary image URL or first image if none primary."""
        try:
            return self.images.filter(is_primary=True).first() or self.images.first()  # type: ignore
        except:
            return None

    @property
    def has_variants(self):
        """Checks if product has multiple variants."""
        try:
            return self.variants.count() > 1  # type: ignore
        except:
            return False

    @property
    def total_stock(self):
        """Aggregates total stock across all variants."""
        try:
            return sum(variant.total_stock for variant in self.variants.all())  # type: ignore
        except:
            return 0

    @property
    def min_price(self):
        """Minimum price across variants (considering discount)."""
        try:
            prices = [variant.final_price for variant in self.variants.all()]  # type: ignore
            return min(prices) if prices else 0
        except:
            return 0

class ProductImage(models.Model):
    """
    Model for multiple product images.
    - product: ForeignKey to Product.
    - image_url: URL from imgbb.com.
    - is_primary: Mark one as primary for thumbnails/lists.
    Uploaded via admin form (file -> imgbb -> save URL).
    """
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name=_("Product"))
    image_url = models.URLField(verbose_name=_("Image URL"))
    is_primary = models.BooleanField(default=False, verbose_name=_("Is Primary"))

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        return f"Image for {self.product.name}"

class Variant(models.Model):
    """
    Model for product variations (e.g., color, size).
    - product: ForeignKey to Product.
    - name: Variant name (e.g., "Red - Large").
    - attributes: JSON dict (e.g., {"color": "red", "size": "large"}).
    - price: Base price for this variant.
    - discount_price: Optional discount price.
    Stock managed via Stock model (multiple per variant for different buying prices).
    """
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE, verbose_name=_("Product"))
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    attributes = models.JSONField(default=dict, blank=True, verbose_name=_("Attributes"))  # e.g., {"color": "red"}
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Price"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_("Discount Price"))

    class Meta:
        verbose_name = _("Variant")
        verbose_name_plural = _("Variants")
        unique_together = ('product', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Returns discount_price if set, else price."""
        return self.discount_price or self.price

    @property
    def total_stock(self):
        """Sum of quantities from all Stock entries for this variant."""
        try:
            return sum(stock.quantity for stock in self.stocks.all() if stock.quantity > 0)  # type: ignore
        except:
            return 0

class Stock(models.Model):
    """
    Model for stock entries. Allows multiple entries per variant with different buying prices (FIFO usage).
    - variant: ForeignKey to Variant.
    - quantity: Current quantity.
    - buying_price: Cost price for this batch.
    - created_at: Timestamp for FIFO ordering.
    Updated via signals when orders are placed (reduce from oldest stock).
    """
    variant = models.ForeignKey(Variant, related_name='stocks', on_delete=models.CASCADE, verbose_name=_("Variant"))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Quantity"))
    buying_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Buying Price"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Stock")
        verbose_name_plural = _("Stocks")
        ordering = ['created_at']  # Oldest first for FIFO

    def __str__(self):
        return f"Stock for {self.variant} ({self.quantity} units)"

class Bundle(models.Model):
    """
    Model for product bundles (multiple products at discounted price).
    - name: Bundle name.
    - slug: Auto-slug.
    - description: Details.
    - products: M2M with Product (can include quantities via through model if needed).
    - bundle_price: Total price for bundle.
    - discount_price: Optional discounted bundle price.
    Treated as a special item in cart/orders.
    """
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = BleachField(verbose_name=_("Description"))
    products = models.ManyToManyField(Product, related_name='bundles', verbose_name=_("Products"))
    bundle_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name=_("Bundle Price"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_("Discount Price"))

    class Meta:
        verbose_name = _("Bundle")
        verbose_name_plural = _("Bundles")
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def final_price(self):
        return self.discount_price or self.bundle_price

class Review(models.Model):
    """
    Model for product reviews and ratings.
    - product: ForeignKey to Product.
    - user: ForeignKey to User.
    - rating: 1-5 stars.
    - comment: Text review.
    - created_at: Timestamp.
    Only allowed after purchase (enforced in views/forms).
    """
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name=_("Product"))
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE, verbose_name=_("User"))
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_("Rating"))
    comment = BleachField(verbose_name=_("Comment"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user} for {self.product}"

# Signal to create default variant for new products
@receiver(post_save, sender=Product)
def create_default_variant(sender, instance, created, **kwargs):
    """
    Signal: On product creation, if no variants, create a default one with product's base price logic.
    Assumes product doesn't have price field; variants handle pricing.
    For simplicity, default variant uses a placeholder price (edit in admin).
    """
    if created and not instance.variants.exists():  # type: ignore
        Variant.objects.create(
            product=instance,
            name="Default",
            price=0.00,  # Placeholder; superuser sets in admin
            attributes={}
        )