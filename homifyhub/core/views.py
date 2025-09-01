from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product
from django.shortcuts import render
from django.contrib.auth.forms import PasswordResetForm
from .forms import ContactForm
from django.urls import reverse_lazy
from django.contrib import messages


class HomeView(TemplateView):
    """
    View for homepage.
    Template: core/home.html
    Context: featured_products, banners, top_notification.
    """

    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Import here to avoid circular imports
        from site_settings.models import Banner, TopNotification

        context["featured_products"] = Product.objects.filter(
            variants__discount_price__isnull=False
        ).distinct()[:8]

        context["banners"] = Banner.objects.filter(is_active=True)[:5]

        try:
            context["top_notification"] = TopNotification.objects.filter(
                is_active=True
            ).first()
        except:
            context["top_notification"] = None

        return context


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    View for user dashboard (overview for customers).
    Template: core/dashboard.html
    Context: recent orders, wishlist count.
    """

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from orders.models import Order
        from carts.models import Wishlist

        context["recent_orders"] = Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")[:5]
        try:
            wishlist = Wishlist.objects.get(user=self.request.user)
            context["wishlist_count"] = wishlist.products.count()
        except Wishlist.DoesNotExist:
            context["wishlist_count"] = 0
        return context


class AboutView(TemplateView):
    """
    View for about page.
    Template: about.html
    """

    template_name = "about.html"


def custom_404(request, exception):
    return render(request, "404.html", status=404)


def custom_500(request):
    return render(request, "500.html", status=500)


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        # Send email or save message (extend with core.utils.send_notification)
        messages.success(self.request, "Thank you for your message!")
        return super().form_valid(form)


class ForgotPasswordView(FormView):
    """
    View for forgot password functionality.
    Template: forgot_password.html
    """

    template_name = "forgot_password.html"
    form_class = PasswordResetForm
    success_url = reverse_lazy("core:home")

    def form_valid(self, form):
        # Send password reset email
        messages.success(
            self.request, "Password reset instructions have been sent to your email!"
        )
        return super().form_valid(form)


class PrivacyPolicyView(TemplateView):
    """View for privacy policy page."""

    template_name = "core/privacy_policy.html"


class TermsOfServiceView(TemplateView):
    """View for terms of service page."""

    template_name = "core/terms_of_service.html"


class ShippingPolicyView(TemplateView):
    """View for shipping policy page."""

    template_name = "core/shipping_policy.html"


class ReturnsView(TemplateView):
    """View for returns policy page."""

    template_name = "core/returns.html"


class HelpCenterView(TemplateView):
    """View for help center page."""

    template_name = "core/help_center.html"


class CareersView(TemplateView):
    """View for careers page."""

    template_name = "core/careers.html"


class OurStoryView(TemplateView):
    """View for our story page."""

    template_name = "core/our_story.html"
