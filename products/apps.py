"""This file is used to configure the app name for the products app."""
from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """
    Configuration for products app
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
