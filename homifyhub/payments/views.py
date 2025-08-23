from django.views.generic import FormView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from orders.models import Order
from .models import Payment
from .forms import PaymentForm


class PaymentFormView(LoginRequiredMixin, FormView):
    """
    View for payment form. Creates Payment for order.
    Template: payments/payment_form.html
    Prefills from last payment.
    After submit, sets status=Pending, redirects to thank_you or status.
    """

    template_name = "payments/payment_form.html"
    form_class = PaymentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.order = get_object_or_404(
            Order, id=self.kwargs["order_id"], user=self.request.user
        )
        kwargs["order"] = self.order
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["order"] = self.order
        return context

    def form_valid(self, form):
        if hasattr(self.order, "payment"):
            messages.error(self.request, "Payment already submitted for this order.")
            return redirect("orders:order_history")
        payment = form.save(commit=False)
        payment.order = self.order
        payment.status = "Pending"
        payment.save()
        messages.success(self.request, "Payment details submitted. Awaiting approval.")
        return redirect("orders:thank_you", pk=getattr(self.order, "id", self.order.pk))


class PaymentStatusView(LoginRequiredMixin, DetailView):
    """
    View for payment status.
    Template: payments/payment_status.html
    Shows status, notes (e.g., cancellation reason).
    """

    template_name = "payments/payment_status.html"
    context_object_name = "payment"

    def get_object(self, queryset=None):
        order = get_object_or_404(
            Order, id=self.kwargs["order_id"], user=self.request.user
        )
        return get_object_or_404(Payment, order=order)
