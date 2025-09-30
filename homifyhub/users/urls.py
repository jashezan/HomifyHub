from django.urls import path
from .views import (
    RegisterView,
    CustomerLoginView,
    SellerLoginView,
    LogoutView,
    ProfileView,
    AddressListView,
    AddressCreateView,
    AddressUpdateView,
    AddressDeleteView,
    VerifyOTPView,
)
from allauth.account.views import LoginView, LogoutView as AllauthLogoutView

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "login/", CustomerLoginView.as_view(), name="login"
    ),  # Main login route for customers
    path(
        "login/customer/", CustomerLoginView.as_view(), name="customer_login"
    ),  # Keep for backward compatibility
    path("login/seller/", SellerLoginView.as_view(), name="seller_login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("addresses/", AddressListView.as_view(), name="address_list"),
    path("addresses/add/", AddressCreateView.as_view(), name="address_create"),
    path(
        "addresses/<int:pk>/edit/", AddressUpdateView.as_view(), name="address_update"
    ),
    path(
        "addresses/<int:pk>/delete/", AddressDeleteView.as_view(), name="address_delete"
    ),
    path("verify-otp/<int:user_id>/", VerifyOTPView.as_view(), name="verify_otp"),
]
