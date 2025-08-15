import django_filters
from django import forms
from .models import Product, Category, Tag


class ProductFilter(django_filters.FilterSet):
    """
    FilterSet for ProductListView. Allows filtering by category, tag, price range, etc.
    Usage in views: queryset = ProductFilter(request.GET, queryset=qs).qs
    - category: By slug.
    - tag: By slug.
    - min_price, max_price: Range.
    - has_discount: Boolean.
    """

    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="Product Name",
        widget=forms.TextInput(
            attrs={"class": "input-field", "placeholder": "Search by name..."}
        ),
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        field_name="categories",
        label="Category",
        empty_label="All Categories",
        widget=forms.Select(attrs={"class": "input-field"}),
    )

    tag = django_filters.ModelChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags",
        label="Tag",
        empty_label="All Tags",
        widget=forms.Select(attrs={"class": "input-field"}),
    )

    min_price = django_filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="gte",
        label="Min Price ($)",
        widget=forms.NumberInput(
            attrs={
                "class": "input-field",
                "placeholder": "0",
                "min": "0",
                "step": "0.01",
            }
        ),
    )

    max_price = django_filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="lte",
        label="Max Price ($)",
        widget=forms.NumberInput(
            attrs={
                "class": "input-field",
                "placeholder": "10000",
                "min": "0",
                "step": "0.01",
            }
        ),
    )

    has_discount = django_filters.BooleanFilter(
        method="filter_has_discount",
        label="On Sale",
        widget=forms.CheckboxInput(attrs={"class": "form-checkbox"}),
    )

    class Meta:
        model = Product
        fields = ["name", "category", "tag", "min_price", "max_price", "has_discount"]

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(variants__discount_price__isnull=False).distinct()
        return queryset
