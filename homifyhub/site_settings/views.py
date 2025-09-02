from django.views.generic import TemplateView
from .models import DeliveryMethod


class PrivacyView(TemplateView):
    """
    View for Privacy Policy page.
    """

    template_name = "site_settings/privacy.html"


class TermsView(TemplateView):
    """
    View for Terms of Service page.
    """

    template_name = "site_settings/terms.html"


class ShippingPolicyView(TemplateView):
    """
    View for Shipping Policy page.
    """

    template_name = "site_settings/shipping_policy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delivery_methods"] = DeliveryMethod.objects.filter(is_active=True)
        return context


class ReturnRefundPolicyView(TemplateView):
    """
    View for Return and Refund Policy page.
    """

    template_name = "site_settings/return_refund_policy.html"


class SitemapView(TemplateView):
    """
    View for Sitemap page.
    """

    template_name = "site_settings/sitemap.html"
