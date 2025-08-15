from django.views.generic import ListView, DetailView, FormView
from django.db.models import Q, Case, When, IntegerField, Sum
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from typing import cast
from .models import Product, Category, Tag, Bundle, Review
from .filters import ProductFilter
from .forms import ReviewForm

# Optional import for order checking
try:
    from orders.models import OrderItem
except ImportError:
    OrderItem = None


class ProductListView(ListView):
    """
    View for listing all products. Supports filtering and search.
    Template: products/product_list.html
    Context: products (filtered), filter (form).
    """

    model = Product
    template_name = "products/product_list.html"
    context_object_name = "products"
    paginate_by = 12  # Pagination for large lists

    def get_queryset(self):
        qs = super().get_queryset()

        # Annotate with total stock and order by stock status (in stock first)
        qs = (
            qs.annotate(total_stock_qty=Sum("variants__stocks__quantity"))
            .annotate(
                stock_status=Case(
                    When(total_stock_qty__gt=0, then=1),
                    When(total_stock_qty=0, then=2),
                    When(total_stock_qty__isnull=True, then=3),
                    default=3,
                    output_field=IntegerField(),
                )
            )
            .order_by("stock_status", "name")
        )

        self.filter = ProductFilter(self.request.GET, queryset=qs)
        return self.filter.qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = self.filter
        context["query"] = self.request.GET.get("q", "")
        return context


class ProductDetailView(DetailView):
    """
    View for product details. Includes related products, reviews, variants, stock status.
    Template: products/product_detail.html
    Context: product, related_products, reviews, form (if can review), variants.
    Handles review form post if user has purchased.
    Related: Same categories or tags, exclude self, limit 4.
    """

    model = Product
    template_name = "products/product_detail.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = cast(Product, self.object)
        context["variants"] = product.variants.all()  # type: ignore
        context["reviews"] = product.reviews.all()  # type: ignore
        context["related_products"] = (
            Product.objects.filter(
                Q(categories__in=product.categories.all()) | Q(tags__in=product.tags.all())  # type: ignore
            )
            .exclude(pk=product.pk)
            .distinct()[:4]
        )  # type: ignore

        # Check if user can review (has purchased)
        if self.request.user.is_authenticated and OrderItem:
            has_purchased = OrderItem.objects.filter(
                order__user=self.request.user,
                product=product,
                order__status="Completed",
            ).exists()
            if (
                has_purchased
                and not Review.objects.filter(
                    product=product, user=self.request.user
                ).exists()
            ):
                context["form"] = ReviewForm()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        product = cast(Product, self.object)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Review submitted successfully!")
            return redirect("products:product_detail", slug=product.slug)  # type: ignore
        else:
            context = self.get_context_data()
            context["form"] = form
            return self.render_to_response(context)


class CategoryDetailView(DetailView):
    """
    View for category products.
    Template: products/category.html
    """

    model = Category
    template_name = "products/category.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = cast(Category, self.object)  # type: ignore
        context["products"] = category.products.all()  # type: ignore
        return context


class TagDetailView(DetailView):
    model = Tag
    template_name = "products/tag.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = cast(Tag, self.object)  # type: ignore
        context["products"] = tag.products.all()  # type: ignore
        return context


class SearchResultsView(ListView):
    """
    View for search results. Searches name, description, tags.
    Template: products/search_results.html
    Query param: q
    """

    model = Product
    template_name = "products/search_results.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            qs = Product.objects.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(tags__name__icontains=query)
                | Q(categories__name__icontains=query)
            ).distinct()

            # Annotate with total stock and order by stock status (in stock first)
            qs = (
                qs.annotate(total_stock_qty=Sum("variants__stocks__quantity"))
                .annotate(
                    stock_status=Case(
                        When(total_stock_qty__gt=0, then=1),
                        When(total_stock_qty=0, then=2),
                        When(total_stock_qty__isnull=True, then=3),
                        default=3,
                        output_field=IntegerField(),
                    )
                )
                .order_by("stock_status", "name")
            )

            return qs
        return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class BundleListView(ListView):
    """
    View for deals (bundles).
    Template: products/deals.html
    """

    model = Bundle
    template_name = "products/deals.html"
    context_object_name = "bundles"


class PromotionListView(ListView):
    """
    View for promotions (products with discounts).
    Template: products/promotions.html
    """

    template_name = "products/promotions.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(variants__discount_price__isnull=False).distinct()
