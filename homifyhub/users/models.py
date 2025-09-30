from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    Custom manager for User model to handle user creation.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_seller", True)  # Superusers are sellers
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    - email: Unique email for login.
    - username: Unique username.
    - phone: Optional phone number for OTP.
    - is_seller: Boolean to distinguish customer vs seller.
    - is_active: For account activation (email/OTP).
    """

    email = models.EmailField(_("Email Address"), unique=True)
    phone = models.CharField(
        max_length=15,
        blank=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Phone number must be valid.")],
        verbose_name=_("Phone Number"),
    )
    is_seller = models.BooleanField(default=False, verbose_name=_("Is Seller"))
    is_active = models.BooleanField(default=False, verbose_name=_("Is Active"))

    objects: UserManager = UserManager()  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def __str__(self):
        return self.email


class Address(models.Model):
    """
    Model for user addresses.
    - user: ForeignKey to User.
    - name: Name for address (e.g., "Home").
    - street: Street address.
    - city, state, postal_code, country: Address components.
    - is_default: Boolean for default address.
    Used in orders for delivery/billing.
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses", verbose_name=_("User")
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    street = models.CharField(max_length=255, verbose_name=_("Street"))
    city = models.CharField(max_length=100, verbose_name=_("City"))
    state = models.CharField(max_length=100, blank=True, verbose_name=_("State"))
    postal_code = models.CharField(max_length=20, verbose_name=_("Postal Code"))
    country = models.CharField(max_length=100, verbose_name=_("Country"))
    is_default = models.BooleanField(default=False, verbose_name=_("Is Default"))

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ["-is_default", "name"]

    def __str__(self):
        return f"{self.name} - {self.user.email}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Ensure only one default address per user
            queryset = Address.objects.filter(user=self.user, is_default=True)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)
            queryset.update(is_default=False)
        super().save(*args, **kwargs)
