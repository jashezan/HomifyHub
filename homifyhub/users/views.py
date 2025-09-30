from django.views.generic import CreateView, FormView, UpdateView, ListView, DeleteView
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django import forms
from typing import cast

from .models import User, Address
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, AddressForm
from core.utils import send_otp, verify_otp  # For OTP activation


class RegisterView(CreateView):
    """
    View for user registration.
    Template: users/register.html
    Sends OTP for activation.
    """

    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:customer_login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Require OTP activation
        user.save()
        send_otp(user)  # Send OTP to phone
        messages.success(
            self.request,
            "Registration successful. Please verify OTP sent to your phone.",
        )
        return redirect("users:verify_otp", user_id=user.id)


class VerifyOTPView(FormView):
    """
    View for OTP verification post-registration.
    """

    template_name = "users/verify_otp.html"
    form_class = forms.Form  # Simple OTP input
    success_url = reverse_lazy("users:customer_login")

    def get_form(self, form_class=None):
        class OTPForm(forms.Form):
            otp = forms.CharField(
                max_length=6,
                label="OTP",
                widget=forms.TextInput(
                    attrs={
                        "placeholder": "Enter 6-digit OTP",
                        "class": "form-control",
                        "maxlength": "6",
                    }
                ),
            )

            def clean_otp(self):
                otp = self.cleaned_data["otp"]
                if not otp.isdigit():
                    raise forms.ValidationError("OTP must contain only digits.")
                if len(otp) != 6:
                    raise forms.ValidationError("OTP must be exactly 6 digits.")
                return otp

        return OTPForm(self.request.POST or None)

    def form_valid(self, form):
        user = get_object_or_404(User, id=self.kwargs["user_id"])

        # Check if user is already active
        if user.is_active:
            messages.info(self.request, "Account is already activated.")
            return redirect("users:customer_login")

        if verify_otp(user, form.cleaned_data["otp"]):
            user.is_active = True
            user.save(update_fields=["is_active"])  # Only update specific field
            messages.success(
                self.request, "Account activated successfully. Please log in."
            )
            return super().form_valid(form)
        else:
            messages.error(self.request, "Invalid or expired OTP. Please try again.")
            return self.form_invalid(form)


class CustomerLoginView(LoginView):
    """
    Login view for customers.
    Template: users/login.html
    Ensures is_seller=False.
    """

    form_class = UserLoginForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = cast(User, form.get_user())  # Type cast for proper type checking
        if user.is_seller:
            messages.error(self.request, "Please use the seller login page.")
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("products:product_list")


class SellerLoginView(LoginView):
    """
    Login view for sellers.
    Template: users/login.html
    Ensures is_seller=True.
    """

    form_class = UserLoginForm
    template_name = "users/login.html"

    def form_valid(self, form):
        user = cast(User, form.get_user())  # Type cast for proper type checking
        if not user.is_seller:
            messages.error(self.request, "Please use the customer login page.")
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("admin:index")  # Seller dashboard or admin


class LogoutView(DjangoLogoutView):
    """
    Logout view for both customers and sellers.
    """

    next_page = reverse_lazy("products:product_list")


class ProfileView(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile.
    Template: users/profile.html
    """

    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return cast(User, self.request.user)


class AddressListView(LoginRequiredMixin, ListView):
    """
    View for listing user addresses.
    Template: users/address_list.html
    """

    model = Address
    template_name = "users/address_list.html"
    context_object_name = "addresses"

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    """
    View for adding a new address.
    Template: users/address_form.html
    """

    form_class = AddressForm
    template_name = "users/address_form.html"
    success_url = reverse_lazy("users:address_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for editing an address.
    Template: users/address_form.html
    """

    model = Address
    form_class = AddressForm
    template_name = "users/address_form.html"
    success_url = reverse_lazy("users:address_list")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting an address.
    """

    model = Address
    success_url = reverse_lazy("users:address_list")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Address deleted successfully.")
        return super().delete(request, *args, **kwargs)
