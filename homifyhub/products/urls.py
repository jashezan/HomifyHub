from django.urls import path
from .views import (
    ProductListView,
    ProductDetailView,
    CategoryDetailView,
    TagDetailView,
    SearchResultsView,
    BundleListView,
    PromotionListView,
)

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="product_list"),
    path("search/", SearchResultsView.as_view(), name="search_results"),
    path("deals/", BundleListView.as_view(), name="deals"),
    path("promotions/", PromotionListView.as_view(), name="promotions"),
    path("category/<slug:slug>/", CategoryDetailView.as_view(), name="category_detail"),
    path("tag/<slug:slug>/", TagDetailView.as_view(), name="tag_detail"),
    path("<slug:slug>/", ProductDetailView.as_view(), name="product_detail"),
]
