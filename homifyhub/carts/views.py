## carts/views.py

from django.views.generic import View, ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Cart, CartItem, Wishlist
from .forms import CartItemForm
from products.models import Product, Variant, Bundle


class CartView(ListView):
    """
    View for cart page.
    Template: carts/cart.html
    Context: cart, items.
    From here, proceed to checkout.
    """

    template_name = "carts/cart.html"
    context_object_name = "items"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            items = getattr(cart, "items", None)
            if items is None:
                return CartItem.objects.filter(cart=cart)
            return items.all()
        else:
            # Handle guest cart from session
            cart_items = self.request.session.get("cart", {})
            items = []
            for product_id, quantity in cart_items.items():
                try:
                    product = Product.objects.get(pk=product_id)

                    # Create a simple object to mimic CartItem
                    class GuestCartItem:
                        def __init__(self, product, quantity):
                            # Get default variant or use product directly
                            if (
                                hasattr(product, "variants")
                                and product.variants.exists()
                            ):
                                self.variant = product.variants.first()
                                self.product = product
                            else:
                                self.variant = None
                                self.product = product
                            self.quantity = quantity
                            self.bundle = None

                        @property
                        def total_price(self):
                            if self.variant and hasattr(self.variant, "final_price"):
                                return self.variant.final_price * self.quantity
                            elif hasattr(self.product, "min_price"):
                                return self.product.min_price * self.quantity
                            else:
                                return 0

                    items.append(GuestCartItem(product, quantity))
                except Product.DoesNotExist:
                    continue
            return items

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            context["cart"] = cart
        else:
            # Create a simple cart object for guests
            class GuestCart:
                def __init__(self, session_cart):
                    self.session_cart = session_cart

                @property
                def total_price(self):
                    total = 0
                    for product_id, quantity in self.session_cart.items():
                        try:
                            product = Product.objects.get(pk=product_id)
                            # Use min_price property from Product
                            total += product.min_price * quantity
                        except (Product.DoesNotExist, AttributeError):
                            continue
                    return total

                @property
                def total_items(self):
                    return sum(self.session_cart.values())

            cart_items = self.request.session.get("cart", {})
            context["cart"] = GuestCart(cart_items)
        return context


class AddToCartView(View):
    """
    View to add product/variant to cart.
    - slug: Product slug (assume default variant for simplicity; extend for variants).
    Check stock, add or update quantity.
    Redirect to cart or product detail.
    """

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        if request.user.is_authenticated:
            # Handle authenticated user cart
            variants = getattr(product, "variants", None)
            if variants is None:
                from products.models import Variant

                variants = Variant.objects.filter(product=product)

            variant = (
                variants.first() if variants else None
            )  # Assume first/default; extend for selection
            if not variant or getattr(variant, "total_stock", 0) <= 0:
                messages.error(request, "Out of stock.")
                return redirect("products:product_detail", slug=slug)

            cart, created = Cart.objects.get_or_create(user=request.user)
            item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
            if not created:
                if item.quantity + 1 > variant.total_stock:
                    messages.error(request, "Insufficient stock.")
                    return redirect("products:product_detail", slug=slug)
                item.quantity += 1
                item.save()
            messages.success(request, "Added to cart.")
        else:
            # Handle guest user cart
            cart = request.session.get("cart", {})
            product_id = str(product.pk)

            if product_id in cart:
                cart[product_id] += 1
            else:
                cart[product_id] = 1

            request.session["cart"] = cart
            request.session.modified = True
            messages.success(request, "Added to cart.")

        return redirect("carts:cart")


class AddBundleToCartView(View):
    """
    Similar to AddToCartView but for bundles.
    Assume bundle stock based on min component stock (implement logic).
    """

    def get(self, request, slug):
        bundle = get_object_or_404(Bundle, slug=slug)

        if request.user.is_authenticated:
            # Check stock for all products in bundle (simplified; assume always available or check min)
            cart, created = Cart.objects.get_or_create(user=request.user)
            item, created = CartItem.objects.get_or_create(cart=cart, bundle=bundle)
            if not created:
                item.quantity += 1
                item.save()
            messages.success(request, "Bundle added to cart.")
        else:
            # For guest users, we'll need to handle bundles differently
            # For now, redirect to login
            messages.info(request, "Please login to add bundles to cart.")
            return redirect("users:login")

        return redirect("carts:cart")


class RemoveFromCartView(View):
    """
    Remove item from cart.
    """

    def get(self, request, pk):
        if request.user.is_authenticated:
            item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
            item.delete()
            messages.success(request, "Item removed from cart.")
        else:
            # For guest users, pk would be product_id in session
            cart = request.session.get("cart", {})
            if str(pk) in cart:
                del cart[str(pk)]
                request.session["cart"] = cart
                request.session.modified = True
                messages.success(request, "Item removed from cart.")

        return redirect("carts:cart")


class UpdateCartItemView(FormView):
    """
    Update item quantity.
    Form: CartItemForm.
    Validate stock.
    """

    form_class = CartItemForm

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please login to update cart items.")
            return redirect("users:login")

        pk = kwargs.get("pk")
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        form = CartItemForm(instance=item)
        return render(
            request, "carts/cart.html", {"form": form, "item": item}
        )  # Partial or AJAX

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "Please login to update cart items.")
            return redirect("users:login")

        pk = kwargs.get("pk")
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        form = CartItemForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save(commit=False)
            variant = getattr(updated_item, "variant", None)
            stock = (
                getattr(variant, "total_stock", 999) if variant else 999
            )  # Assume bundles unlimited
            if updated_item.quantity > stock:
                messages.error(request, "Insufficient stock.")
            else:
                updated_item.save()
                messages.success(request, "Cart updated.")
        return redirect("carts:cart")


class WishlistView(ListView):
    """
    View for wishlist page.
    Template: carts/wishlist.html
    Context: products.
    """

    template_name = "carts/wishlist.html"
    context_object_name = "products"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
            return wishlist.products.all()
        else:
            # Handle guest wishlist from session
            wishlist_items = self.request.session.get("wishlist", [])
            return Product.objects.filter(pk__in=wishlist_items)


class AddToWishlistView(View):
    """
    Add product to wishlist.
    """

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        if request.user.is_authenticated:
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            wishlist.products.add(product)
            messages.success(request, "Added to wishlist.")
        else:
            # Handle guest wishlist
            wishlist = request.session.get("wishlist", [])
            if product.pk not in wishlist:
                wishlist.append(product.pk)
                request.session["wishlist"] = wishlist
                request.session.modified = True
            messages.success(request, "Added to wishlist.")

        return redirect("products:product_detail", slug=slug)


class RemoveFromWishlistView(View):
    """
    Remove from wishlist.
    """

    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        if request.user.is_authenticated:
            wishlist = get_object_or_404(Wishlist, user=request.user)
            wishlist.products.remove(product)
            messages.success(request, "Removed from wishlist.")
        else:
            # Handle guest wishlist
            wishlist = request.session.get("wishlist", [])
            if product.pk in wishlist:
                wishlist.remove(product.pk)
                request.session["wishlist"] = wishlist
                request.session.modified = True
            messages.success(request, "Removed from wishlist.")

        return redirect("carts:wishlist")
