from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Address
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration. Includes email, username, phone.
    """
    phone = forms.CharField(max_length=15, required=False, label="Phone Number")

    class Meta:
        model = User
        fields = ('email', 'username', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('email', css_class='w-full p-2 border rounded'),
            Field('username', css_class='w-full p-2 border rounded'),
            Field('phone', css_class='w-full p-2 border rounded'),
            Field('password1', css_class='w-full p-2 border rounded'),
            Field('password2', css_class='w-full p-2 border rounded'),
            Submit('submit', 'Register', css_class='btn btn-primary')
        )

class UserLoginForm(AuthenticationForm):
    """
    Form for user login. Uses email instead of username.
    """
    username = forms.EmailField(label="Email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='w-full p-2 border rounded'),
            Field('password', css_class='w-full p-2 border rounded'),
            Submit('submit', 'Login', css_class='btn btn-primary')
        )

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile.
    """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('username', css_class='w-full p-2 border rounded'),
            Field('first_name', css_class='w-full p-2 border rounded'),
            Field('last_name', css_class='w-full p-2 border rounded'),
            Field('phone', css_class='w-full p-2 border rounded'),
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )

class AddressForm(forms.ModelForm):
    """
    Form for adding/editing addresses.
    """
    class Meta:
        model = Address
        fields = ('name', 'street', 'city', 'state', 'postal_code', 'country', 'is_default')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name', css_class='w-full p-2 border rounded'),
            Field('street', css_class='w-full p-2 border rounded'),
            Field('city', css_class='w-full p-2 border rounded'),
            Field('state', css_class='w-full p-2 border rounded'),
            Field('postal_code', css_class='w-full p-2 border rounded'),
            Field('country', css_class='w-full p-2 border rounded'),
            Field('is_default', css_class='mt-2'),
            Submit('submit', 'Save Address', css_class='btn btn-primary')
        )