from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import custom_404, custom_500  # Define below

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # For social/auth
    path("", include("core.urls")),
    path("products/", include("products.urls")),
    path("orders/", include("orders.urls")),
    path("carts/", include("carts.urls")),
    path("payments/", include("payments.urls")),
    path("users/", include("users.urls")),
    path("site/", include("site_settings.urls")),
    path("blogs/", include("blogs.urls")),  # Now properly implemented
]

# Serve media/static in dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = custom_404
handler500 = custom_500
