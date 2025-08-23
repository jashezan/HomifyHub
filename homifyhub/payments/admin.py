from django.contrib import admin
from django.utils.html import format_html
from .models import Payment
from orders.models import Order  # For updating order status


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Admin for Payment. Seller approves/rejects, adds notes.
    - List: order, method, amount, status, is_confirmed, created_at.
    - Filters: status, method.
    - Search: order__order_number, transaction_id.
    - Actions: Approve payments, Reject payments.
    Approving sets is_confirmed=True, status=Completed, updates order to Processing.
    """

    list_display = (
        "order",
        "method",
        "amount",
        "status",
        "is_confirmed",
        "created_at",
        "view_proof",
    )
    list_filter = ("status", "method", "is_confirmed")
    search_fields = ("order__order_number", "transaction_id")
    actions = ["approve_payments", "reject_payments"]

    def view_proof(self, obj):
        if obj.proof_url:
            return format_html(
                '<a href="{}" target="_blank">View Proof</a>', obj.proof_url
            )
        return "No Proof"

    view_proof.short_description = "Proof"  # type: ignore

    def approve_payments(self, request, queryset):
        for payment in queryset:
            if not payment.is_confirmed:
                payment.is_confirmed = True
                payment.status = "Completed"
                payment.save()
                # Update order
                payment.order.status = "Processing"
                payment.order.save()
                # Send notification/email (assume core.utils.send_notification)
                from core.utils import send_notification

                send_notification(
                    payment.order.user,
                    f"Your payment for order {payment.order.order_number} has been approved.",
                )
        self.message_user(request, "Selected payments approved.")

    approve_payments.short_description = "Approve selected payments"  # type: ignore

    def reject_payments(self, request, queryset):
        for payment in queryset:
            if payment.status == "Pending":
                payment.status = "Failed"
                payment.save()
                # Update order
                payment.order.status = "Cancelled"
                payment.order.save()
                # Send notification
                from core.utils import send_notification

                send_notification(
                    payment.order.user,
                    f"Your payment for order {payment.order.order_number} has been rejected.",
                )
        self.message_user(request, "Selected payments rejected.")

    reject_payments.short_description = "Reject selected payments"  # type: ignore
