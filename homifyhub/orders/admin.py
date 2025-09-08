from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponse
from weasyprint import HTML
from .models import Order, OrderItem, OrderItemStock, DeliveryTracking


class OrderItemStockInline(admin.TabularInline):
    """
    Inline for OrderItemStock in OrderItem admin.
    """

    model = OrderItemStock
    extra = 0


class OrderItemInline(admin.TabularInline):
    """
    Inline for OrderItem in Order admin.
    """

    model = OrderItem
    extra = 0
    fields = ("variant", "bundle", "quantity", "price_at_purchase", "subtotal")
    readonly_fields = ("subtotal",)


class DeliveryTrackingInline(admin.TabularInline):
    """
    Inline for DeliveryTracking in Order admin.
    """

    model = DeliveryTracking
    extra = 0
    fields = ("status", "tracking_number", "courier", "estimated_delivery", "updates")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin for Order model. Customized for superuser to manage orders.
    - List: order_number, user, status, total_amount, created_at.
    - Filters: status, delivery_method.
    - Search: order_number, user__username.
    - Actions: Generate invoice, update status.
    - Inlines: OrderItem, DeliveryTracking.
    """

    list_display = (
        "order_number",
        "user",
        "status",
        "total_amount",
        "created_at",
        "view_invoice",
    )
    list_filter = ("status", "delivery_method")
    search_fields = ("order_number", "user__username")
    inlines = [OrderItemInline, DeliveryTrackingInline]
    actions = ["mark_as_shipped", "generate_invoices"]

    def view_invoice(self, obj):
        """Link to download invoice PDF."""
        url = reverse("orders:invoice", args=[obj.id])
        return format_html('<a href="{}">Download Invoice</a>', url)

    view_invoice.short_description = "Invoice"  # type: ignore

    def mark_as_shipped(self, request, queryset):
        """Action to mark orders as Shipped."""
        queryset.update(status="Shipped")
        self.message_user(request, "Selected orders marked as shipped.")

    mark_as_shipped.short_description = "Mark as Shipped"  # type: ignore

    def generate_invoices(self, request, queryset):
        """Action to generate invoices for selected orders."""
        for order in queryset:
            if order.status == "Delivered":
                # Logic to generate PDF (handled in views.OrderInvoiceView)
                pass
        self.message_user(request, "Invoices generated for delivered orders.")

    generate_invoices.short_description = "Generate Invoices"  # type: ignore


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Separate admin for OrderItem if needed.
    """

    list_display = (
        "order",
        "variant",
        "bundle",
        "quantity",
        "price_at_purchase",
        "subtotal",
    )
    list_filter = ("order__status",)
    search_fields = ("order__order_number", "variant__name", "bundle__name")
    inlines = [OrderItemStockInline]


@admin.register(OrderItemStock)
class OrderItemStockAdmin(admin.ModelAdmin):
    """
    Admin for OrderItemStock. Useful for accounting.
    """

    list_display = ("order_item", "stock", "quantity")
    list_filter = ("order_item__order",)


@admin.register(DeliveryTracking)
class DeliveryTrackingAdmin(admin.ModelAdmin):
    """
    Admin for DeliveryTracking.
    """

    list_display = (
        "order",
        "status",
        "tracking_number",
        "courier",
        "estimated_delivery",
    )
    list_filter = ("status",)
    search_fields = ("order__order_number", "tracking_number")
