from django.urls import path
from .views import (
    HomeView,
    DashboardView,
    AboutView,
    ForgotPasswordView,
    ContactView,
    PrivacyPolicyView,
    TermsOfServiceView,
    ShippingPolicyView,
    ReturnsView,
    HelpCenterView,
    CareersView,
    OurStoryView,
)

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("about/", AboutView.as_view(), name="about"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    # Footer pages
    path("privacy/", PrivacyPolicyView.as_view(), name="privacy_policy"),
    path("terms/", TermsOfServiceView.as_view(), name="terms_of_service"),
    path("shipping/", ShippingPolicyView.as_view(), name="shipping_policy"),
    path("returns/", ReturnsView.as_view(), name="returns"),
    path("help/", HelpCenterView.as_view(), name="help_center"),
    path("careers/", CareersView.as_view(), name="careers"),
    path("story/", OurStoryView.as_view(), name="our_story"),
]
