from django.contrib import admin
from django import forms
from .models import Category, Tag, Product, ProductImage, Variant, Stock, Bundle, Review
from core.utils import imgbb_upload  # Assuming core/utils.py has the upload function

class ProductImageInline(admin.TabularInline):
    """
    Inline for adding multiple images to Product in admin.
    Handles file upload to imgbb and saves URL.
    """
    model = ProductImage
    extra = 1
    fields = ('image_url', 'is_primary')

class VariantInline(admin.TabularInline):
    """
    Inline for variants in Product admin.
    """
    model = Variant
    extra = 1

class StockInline(admin.TabularInline):
    """
    Inline for stocks in Variant admin.
    """
    model = Stock
    extra = 1

class ProductAdminForm(forms.ModelForm):
    """
    Custom form for Product admin. If needed, can handle uploads here.
    """
    class Meta:
        model = Product
        fields = '__all__'

class ProductImageAdminForm(forms.ModelForm):
    """
    Form for ProductImage. Includes a FileField for upload, then uploads to imgbb.
    """
    upload_image = forms.FileField(required=False, label="Upload Image")

    class Meta:
        model = ProductImage
        fields = ('product', 'image_url', 'is_primary', 'upload_image')

    def save(self, commit=True):
        instance = super().save(commit=False)
        upload_file = self.cleaned_data.get('upload_image')
        if upload_file:
            # Upload to imgbb and set image_url
            instance.image_url = imgbb_upload(upload_file)
        if commit:
            instance.save()
        return instance

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin for Category. List name, slug, parent.
    Search by name.
    """
    list_display = ('name', 'slug', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin for Tag.
    """
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin for Product. Customized for superuser management.
    Inlines: Images, Variants.
    List: name, categories, total_stock.
    Filters: categories, tags.
    Actions: e.g., mark as featured (if added field).
    """
    form = ProductAdminForm
    list_display = ('name', 'slug', 'get_categories', 'total_stock', 'min_price')
    list_filter = ('categories', 'tags')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, VariantInline]

    def get_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    get_categories.short_description = "Categories"  # type: ignore

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Separate admin for images if needed. Uses custom form for uploads.
    """
    form = ProductImageAdminForm
    list_display = ('product', 'image_url', 'is_primary')

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    """
    Admin for Variant. Inlines: Stocks.
    """
    list_display = ('product', 'name', 'price', 'discount_price', 'total_stock')
    inlines = [StockInline]

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    """
    Admin for Stock. For managing inventory.
    """
    list_display = ('variant', 'quantity', 'buying_price', 'created_at')
    list_filter = ('variant__product',)

@admin.register(Bundle)
class BundleAdmin(admin.ModelAdmin):
    """
    Admin for Bundles.
    """
    list_display = ('name', 'bundle_price', 'discount_price')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('products',)  # For M2M selection

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin for Reviews. Superuser can moderate.
    """
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'product')
    search_fields = ('user__username', 'product__name')