from django.contrib import admin
from django.shortcuts import redirect
from .models import (
    SiteSettings,
    DeliveryMethod,
    Coupon,
    PaymentMethod,
    Banner,
    TopNotification,
    FooterLink,
    ContactInfo,
)
from orders.models import Order
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages

try:
    from weasyprint import HTML
except ImportError:
    HTML = None


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin for SiteSettings (singleton).
    - List: site_name, low_stock_threshold, contact_email.
    - Ensure only one instance.
    """

    list_display = (
        "site_name",
        "low_stock_threshold",
        "contact_email",
        "contact_phone",
        "default_currency",
    )
    actions = None  # Disable bulk actions for singleton

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    """
    Admin for DeliveryMethod.
    - List: name, cost, estimated_days, is_active.
    - Search: name.
    """

    list_display = ("name", "cost", "estimated_days", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Admin for Coupon.
    - List: code, discount_amount, is_active, valid_until.
    - Search: code.
    """

    list_display = ("code", "discount_amount", "is_active", "valid_from", "valid_until")
    list_filter = ("is_active",)
    search_fields = ("code",)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """
    Admin for PaymentMethod.
    - List: name, is_active.
    - Search: name.
    """

    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


class SalesReportAdmin(admin.ModelAdmin):
    """
    Custom admin view for generating sales reports.
    - Not tied to a model; uses Order data.
    - Action: Generate PDF report.
    """

    change_list_template = "admin/sales_report.html"

    def get_urls(self):
        from django.urls import path

        urls = super().get_urls()
        custom_urls = [
            path(
                "sales-report/",
                self.admin_site.admin_view(self.sales_report_view),
                name="sales_report",
            ),
        ]
        return custom_urls + urls

    def sales_report_view(self, request):
        """
        Generate sales report PDF.
        Aggregates order data (total sales, completed orders, etc.).
        """
        if not getattr(request.user, "is_seller", False):
            messages.error(request, "Only sellers can access sales reports.")
            return redirect("admin:index")

        orders = Order.objects.filter(status="Delivered")
        total_sales = sum(getattr(order, "total_amount", 0) for order in orders)
        total_orders = orders.count()
        context = {
            "orders": orders,
            "total_sales": total_sales,
            "total_orders": total_orders,
            "site_settings": SiteSettings.load(),
        }
        html_string = render_to_string("admin/sales_report.html", context)

        if HTML is not None:
            html = HTML(string=html_string)
            pdf = html.write_pdf()
            if pdf:
                response = HttpResponse(content_type="application/pdf")
                response["Content-Disposition"] = (
                    'attachment; filename="sales_report.pdf"'
                )
                response.write(pdf)
                return response

        # Fallback to HTML if WeasyPrint not available
        return HttpResponse(html_string)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    """
    Admin for Banner model.
    """

    list_display = ("title", "is_active", "order", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title", "subtitle")
    ordering = ("order", "-created_at")
    list_editable = ("is_active", "order")


@admin.register(TopNotification)
class TopNotificationAdmin(admin.ModelAdmin):
    """
    Admin for TopNotification model.
    """

    list_display = ("message", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("message",)
    ordering = ("-created_at",)
    list_editable = ("is_active",)


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    """
    Admin for FooterLink model.
    """

    list_display = ("title", "section", "is_active", "order")
    list_filter = ("section", "is_active", "is_external")
    search_fields = ("title", "url")
    ordering = ("section", "order")
    list_editable = ("is_active", "order")


@admin.register(ContactInfo)
class ContactInfoAdmin(admin.ModelAdmin):
    """
    Admin for ContactInfo (singleton).
    """

    list_display = ("address", "phone", "email", "working_hours")

    def has_add_permission(self, request):
        return not ContactInfo.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# Note: SalesReportAdmin is a custom admin view and should be registered through URL patterns
# rather than through admin.site.register() since it's not tied to a specific model
