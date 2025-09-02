from django.urls import path
from .views import PrivacyView, TermsView, ShippingPolicyView, ReturnRefundPolicyView, SitemapView

app_name = 'site_settings'

urlpatterns = [
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('shipping-policy/', ShippingPolicyView.as_view(), name='shipping_policy'),
    path('return-refund-policy/', ReturnRefundPolicyView.as_view(), name='return_refund_policy'),
    path('sitemap/', SitemapView.as_view(), name='sitemap'),
]