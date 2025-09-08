from django.views.generic import View, ListView, DetailView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from typing import cast

from .models import Order, OrderItem, DeliveryTracking
from .forms import OrderCreateForm, OrderCancelForm
from core.utils import send_otp  # For OTP generation

# Optional imports for cart and payment functionality
try:
    from carts.models import Cart, CartItem
except ImportError:
    Cart = None
    CartItem = None

try:
    from payments.models import Payment
except ImportError:
    Payment = None

try:
    from site_settings.models import DeliveryMethod
except ImportError:
    DeliveryMethod = None

try:
    from weasyprint import HTML
except ImportError:
    HTML = None


class OrderCreateView(LoginRequiredMixin, FormView):
    """
    View for checkout process. Creates order from cart.
    Template: orders/checkout.html
    Steps:
    1. Validate cart (stock, items).
    2. Send OTP to user's phone.
    3. Validate form (delivery, address, OTP, terms).
    4. Create Order, OrderItems, link to Payment.
    5. Clear cart, redirect to payment.
    """

    template_name = "orders/checkout.html"
    form_class = OrderCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if Cart:
            try:
                cart = get_object_or_404(Cart, user=self.request.user)
                context["cart"] = cart
                context["cart_items"] = cart.items.all()  # type: ignore
            except:
                context["cart"] = None
                context["cart_items"] = []
        else:
            context["cart"] = None
            context["cart_items"] = []

        if DeliveryMethod:
            context["delivery_methods"] = DeliveryMethod.objects.all()
        else:
            context["delivery_methods"] = []
        return context

    def get(self, request, *args, **kwargs):
        # Check if user has phone number (use getattr for safety)
        if not getattr(request.user, "phone", None):
            messages.error(request, "Please add a phone number to your profile.")
            return redirect("users:profile")
        # Send OTP
        send_otp(request.user)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        # Check if Cart is available
        if not Cart:
            messages.error(request, "Cart functionality is not available.")
            return redirect("products:product_list")

        try:
            cart = get_object_or_404(Cart, user=request.user)
        except:
            messages.error(request, "Your cart is empty.")
            return redirect("products:product_list")

        if not cart.items.exists():  # type: ignore
            messages.error(request, "Your cart is empty.")
            return redirect("carts:cart")

        if form.is_valid():
            # Validate stock
            for item in cart.items.all():  # type: ignore
                if item.variant and item.quantity > item.variant.total_stock:
                    messages.error(request, f"Insufficient stock for {item.variant}.")
                    return redirect("carts:cart")

            # Create order - cast form to ModelForm for save method
            from django.forms import ModelForm

            if isinstance(form, ModelForm):
                order = form.save(commit=False)
                order.user = request.user
                order.total_amount = sum(item.subtotal for item in cart.items.all())  # type: ignore
                if form.cleaned_data.get("coupon_code"):
                    order.coupon = form.cleaned_data["coupon_code"]
                    order.total_amount -= (
                        order.coupon.discount_amount
                    )  # Assuming Coupon has discount_amount
                order.save()

                # Create order items
                for item in cart.items.all():  # type: ignore
                    OrderItem.objects.create(
                        order=order,
                        variant=item.variant,
                        bundle=item.bundle,
                        quantity=item.quantity,
                        price_at_purchase=(
                            item.variant.final_price
                            if item.variant
                            else item.bundle.final_price
                        ),
                        customization=getattr(item, "customization", {}),
                    )

                # Clear cart
                cart.items.all().delete()  # type: ignore

                # Create Payment (redirect to payment form)
                return redirect("payments:payment_form", order_id=order.id)
            else:
                messages.error(request, "Invalid form type.")
                return redirect("orders:checkout")
        return self.form_invalid(form)


class OrderSummaryView(LoginRequiredMixin, DetailView):
    """
    View for order summary before payment.
    Template: orders/order_summary.html
    Context: order, items, payment (if exists).
    """

    model = Order
    template_name = "orders/order_summary.html"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = cast(Order, self.object)  # type: ignore
        context["items"] = order.items.all()  # type: ignore
        context["payment"] = getattr(order, "payment", None)
        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    """
    View for user's order history.
    Template: orders/order_history.html
    Context: orders.
    """

    model = Order
    template_name = "orders/order_history.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderTrackingView(LoginRequiredMixin, DetailView):
    """
    View for tracking order and delivery status.
    Template: orders/order_tracking.html
    Context: order, tracking.
    """

    model = Order
    template_name = "orders/order_tracking.html"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = cast(Order, self.object)  # type: ignore
        context["tracking"] = getattr(order, "tracking", None)
        return context


class OrderCancelView(LoginRequiredMixin, FormView):
    """
    View for cancelling an order (if payment not approved).
    Template: orders/order_cancel.html
    """

    template_name = "orders/order_cancel.html"
    form_class = OrderCancelForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = get_object_or_404(
            Order, pk=self.kwargs["pk"], user=self.request.user
        )
        return context

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs["pk"], user=request.user)
        if not order.is_cancellable:
            messages.error(request, "Order cannot be cancelled.")
            return redirect("orders:order_history")

        form = self.get_form()
        if form.is_valid():
            order.status = "Cancelled"
            order.notes += f"\nCancelled: {form.cleaned_data['reason']}"
            order.save()
            # Notify payment cancellation if exists
            payment = getattr(order, "payment", None)
            if payment:
                payment.status = "Cancelled"
                payment.notes += f"\nOrder cancelled: {form.cleaned_data['reason']}"
                payment.save()
            messages.success(request, "Order cancelled successfully.")
            return redirect("orders:order_history")
        return self.form_invalid(form)


class OrderInvoiceView(LoginRequiredMixin, View):
    """
    View to generate and download invoice PDF.
    Uses weasyprint to render invoice.html to PDF.
    """

    def get(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=self.kwargs["pk"], user=request.user)
        if order.status != "Delivered":
            messages.error(request, "Invoice available only for delivered orders.")
            return redirect("orders:order_history")

        if not HTML:
            messages.error(request, "PDF generation is not available.")
            return redirect("orders:order_history")

        html_string = render_to_string(
            "orders/invoice.html",
            {"order": order, "items": order.items.all()},  # type: ignore
        )
        html = HTML(string=html_string)
        pdf = html.write_pdf()

        if pdf:
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="invoice_{order.order_number}.pdf"'
            )
            response.write(pdf)
            return response
        else:
            messages.error(request, "Failed to generate PDF.")
            return redirect("orders:order_history")


class ThankYouView(LoginRequiredMixin, DetailView):
    """
    View for thank you page after order placement.
    Template: orders/thank_you.html
    """

    model = Order
    template_name = "orders/thank_you.html"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
