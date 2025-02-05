"""
Product model
"""

from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    """
    Product model
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.name)
