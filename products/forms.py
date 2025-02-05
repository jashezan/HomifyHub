"""
This file is used to create a form for the Product model.
"""
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    """
    Product form
    """
    class Meta:
        """
        Meta class
        """
        model = Product
        fields = ['name', 'description', 'price']
