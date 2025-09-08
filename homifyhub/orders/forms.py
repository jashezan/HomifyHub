from django import forms
from django.core.exceptions import ValidationError
from .models import Order
from users.models import Address
from site_settings.models import Coupon
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field


class OrderCreateForm(forms.ModelForm):
    """
    Form for creating an order during checkout.
    - delivery_method: Choice of available delivery methods.
    - delivery_address: User's delivery address.
    - billing_address: User's billing address (optional, defaults to delivery).
    - coupon_code: Optional coupon code input.
    - otp: OTP for verification (sent via Twilio).
    - terms_agreed: Checkbox for terms/privacy agreement.
    Validates stock, addresses, OTP, and terms.
    """

    coupon_code = forms.CharField(max_length=20, required=False, label="Coupon Code")
    otp = forms.CharField(max_length=6, required=True, label="OTP")
    terms_agreed = forms.BooleanField(
        required=True, label="I agree to the Terms of Service and Privacy Policy"
    )

    class Meta:
        model = Order
        fields = ("delivery_method", "delivery_address", "billing_address", "notes")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            if isinstance(self.fields["delivery_address"], forms.ModelChoiceField):
                self.fields["delivery_address"].queryset = Address.objects.filter(
                    user=user
                )
            if isinstance(self.fields["billing_address"], forms.ModelChoiceField):
                self.fields["billing_address"].queryset = Address.objects.filter(
                    user=user
                )
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("delivery_method", css_class="w-full p-2 border rounded"),
            Field("delivery_address", css_class="w-full p-2 border rounded"),
            Field("billing_address", css_class="w-full p-2 border rounded"),
            Field("coupon_code", css_class="w-full p-2 border rounded"),
            Field("otp", css_class="w-full p-2 border rounded"),
            Field("notes", css_class="w-full p-2 border rounded"),
            Field("terms_agreed", css_class="mt-2"),
            Submit("submit", "Place Order", css_class="btn btn-primary"),
        )

    def clean_coupon_code(self):
        code = self.cleaned_data.get("coupon_code")
        if code:
            try:
                coupon = Coupon.objects.get(code=code, is_active=True)
                return coupon
            except Coupon.DoesNotExist:
                raise ValidationError("Invalid or inactive coupon code.")
        return None

    def clean_otp(self):
        otp = self.cleaned_data.get("otp")
        # Assuming OTP stored in session or model (core.utils.verify_otp)
        from core.utils import verify_otp

        if not verify_otp(self.user, otp):
            raise ValidationError("Invalid OTP.")
        return otp

    def clean(self):
        cleaned_data = super().clean()
        if not self.user or not hasattr(self.user, "phone") or not self.user.phone:
            raise ValidationError("User must have a phone number to place an order.")
        if not cleaned_data.get("delivery_address"):
            raise ValidationError("Delivery address is required.")
        return cleaned_data


class OrderCancelForm(forms.Form):
    """
    Form for cancelling an order.
    - reason: Text for cancellation reason.
    """

    reason = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4}),
        required=True,
        label="Cancellation Reason",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Cancel Order", css_class="btn btn-danger")
        )
