## carts/forms.py

from django import forms
from .models import CartItem
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class CartItemForm(forms.ModelForm):
    """
    Form for adding/editing cart items.
    - quantity: Integer.
    - customization: Optional JSON (handled in view).
    """
    class Meta:
        model = CartItem
        fields = ('quantity',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update', css_class='btn btn-primary'))