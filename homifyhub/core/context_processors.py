from site_settings.models import (
    SiteSettings,
    ContactInfo,
    FooterLink,
)  # Assuming exists


def site_settings(request):
    """
    Context processor to provide site-wide settings.
    Adds site_settings, contact_info, footer links and cart/wishlist item counts to all templates.
    """
    context = {
        "site_settings": (
            SiteSettings.objects.first() if SiteSettings.objects.exists() else None
        ),
        "contact_info": ContactInfo.load(),
        "footer_company_links": FooterLink.objects.filter(
            section="company", is_active=True
        ),
        "footer_support_links": FooterLink.objects.filter(
            section="support", is_active=True
        ),
        "footer_legal_links": FooterLink.objects.filter(
            section="legal", is_active=True
        ),
        "cart_item_count": 0,
        "wishlist_item_count": 0,
    }

    if request.user.is_authenticated:
        # Cart count for authenticated users
        from carts.models import Cart, Wishlist

        try:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            context["cart_item_count"] = cart.item_count
        except:
            context["cart_item_count"] = 0

        # Wishlist count for authenticated users
        try:
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            context["wishlist_item_count"] = wishlist.products.count()
        except:
            context["wishlist_item_count"] = 0
    else:
        # Cart count for guest users
        cart_items = request.session.get("cart", {})
        context["cart_item_count"] = sum(cart_items.values())

        # Wishlist count for guest users
        wishlist_items = request.session.get("wishlist", [])
        context["wishlist_item_count"] = len(wishlist_items)

    return context
