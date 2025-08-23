from django import forms
from .models import Payment
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from core.utils import imgbb_upload  # For proof upload


class PaymentForm(forms.ModelForm):
    """
    Form for manual payment entry. Prefills from last successful payment except txid.
    - proof: FileField for upload (to imgbb).
    Validation: Amount matches order.total_amount.
    """

    proof = forms.FileField(required=False, label="Payment Proof")

    class Meta:
        model = Payment
        fields = ("from_account", "method", "amount", "transaction_id", "note", "proof")
        widgets = {
            "amount": forms.NumberInput(
                attrs={"readonly": "readonly"}
            ),  # Set in initial
        }

    def __init__(self, *args, order=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.order = order
        if order:
            self.fields["amount"].initial = order.total_amount
        # Prefill from last successful payment
        if order and order.user:
            last_payment = (
                Payment.objects.filter(order__user=order.user, status="Completed")
                .order_by("-created_at")
                .first()
            )
            if last_payment:
                self.fields["from_account"].initial = last_payment.from_account
                self.fields["method"].initial = last_payment.method
                self.fields["note"].initial = last_payment.note

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(
            Submit("submit", "Submit Payment", css_class="btn btn-primary")
        )

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if self.order and amount != self.order.total_amount:
            raise forms.ValidationError("Amount must match order total.")
        return amount

    def save(self, commit=True):
        instance = super().save(commit=False)
        proof_file = self.cleaned_data.get("proof")
        if proof_file:
            instance.proof_url = imgbb_upload(proof_file)
        if commit:
            instance.save()
        return instance
