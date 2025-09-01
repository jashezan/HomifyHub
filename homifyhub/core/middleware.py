from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class EnsureActiveUserMiddleware:
    """
    Middleware to ensure only active users can access protected views.
    Redirects inactive users to login with message.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            if request.path not in [reverse('users:verify_otp', kwargs={'user_id': request.user.id}),
                                    reverse('users:logout')]:
                messages.error(request, "Please verify your account to continue.")
                return redirect('users:verify_otp', user_id=request.user.id)
        return self.get_response(request)

class SellerAccessMiddleware:
    """
    Middleware to restrict seller-only views (e.g., admin) to sellers.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/') and request.user.is_authenticated and not request.user.is_seller:
            messages.error(request, "Only sellers can access the admin dashboard.")
            return redirect('products:product_list')
        return self.get_response(request)