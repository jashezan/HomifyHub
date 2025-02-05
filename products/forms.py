"""
Forms for products app
"""

from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    """
    Product form with Bootstrap styling
    """

    class Meta:
        """
        Meta class for ProductForm
        """

        model = Product
        fields = ["name", "description", "price"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter product name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 20,
                    "placeholder": "Enter product description",
                }
            ),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Enter price"}
            ),
        }
