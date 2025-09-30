from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin for User model. Extends Django's UserAdmin.
    - List: email, username, is_seller, is_active, date_joined.
    - Filters: is_seller, is_active.
    - Search: email, username.
    - Fieldsets: Customized for user/seller fields.
    """
    list_display = ('email', 'username', 'is_seller', 'is_active', 'date_joined')
    list_filter = ('is_seller', 'is_active', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_seller', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'phone', 'password1', 'password2', 'is_seller', 'is_active'),
        }),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """
    Admin for Address model.
    - List: user, name, street, city, is_default.
    - Search: user__email, name, city.
    """
    list_display = ('user', 'name', 'street', 'city', 'is_default')
    search_fields = ('user__email', 'name', 'city')
    list_filter = ('is_default',)