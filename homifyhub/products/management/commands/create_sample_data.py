from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Category, Tag, Product, Variant, Stock
from faker import Faker
import random

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Create sample data for testing"

    def handle(self, *args, **options):
        # Create categories
        categories_data = [
            {"name": "Living Room", "slug": "living-room"},
            {"name": "Bedroom", "slug": "bedroom"},
            {"name": "Kitchen & Dining", "slug": "kitchen"},
            {"name": "Home Decor", "slug": "decor"},
            {"name": "Office", "slug": "office"},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={"name": cat_data["name"], "description": fake.text()},
            )
            categories.append(category)
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create tags
        tags_data = [
            "Modern",
            "Vintage",
            "Minimalist",
            "Luxury",
            "Affordable",
            "Eco-Friendly",
            "Handmade",
        ]
        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name, defaults={"slug": tag_name.lower().replace(" ", "-")}
            )
            tags.append(tag)
            if created:
                self.stdout.write(f"Created tag: {tag.name}")

        # Create products
        products_data = [
            {
                "name": "Modern Sofa Set",
                "category": "living-room",
                "price": 1299.99,
                "discount": 1099.99,
            },
            {
                "name": "Elegant Dining Table",
                "category": "kitchen",
                "price": 899.99,
                "discount": None,
            },
            {
                "name": "Comfortable Office Chair",
                "category": "office",
                "price": 399.99,
                "discount": 299.99,
            },
            {
                "name": "Luxury King Bed",
                "category": "bedroom",
                "price": 1599.99,
                "discount": None,
            },
            {
                "name": "Modern Coffee Table",
                "category": "living-room",
                "price": 299.99,
                "discount": 249.99,
            },
            {
                "name": "Decorative Wall Art",
                "category": "decor",
                "price": 89.99,
                "discount": None,
            },
            {
                "name": "Stylish Bookshelf",
                "category": "office",
                "price": 199.99,
                "discount": None,
            },
            {
                "name": "Comfortable Armchair",
                "category": "living-room",
                "price": 699.99,
                "discount": 599.99,
            },
            {
                "name": "Modern Lamp Set",
                "category": "decor",
                "price": 149.99,
                "discount": None,
            },
            {
                "name": "Wooden Dresser",
                "category": "bedroom",
                "price": 799.99,
                "discount": 699.99,
            },
        ]

        for product_data in products_data:
            # Find category
            category = next(
                (c for c in categories if c.slug == product_data["category"]), None
            )

            product, created = Product.objects.get_or_create(
                name=product_data["name"],
                defaults={
                    "description": fake.text(),
                    "slug": product_data["name"]
                    .lower()
                    .replace(" ", "-")
                    .replace(",", ""),
                },
            )

            if created:
                # Add to category
                if category:
                    product.categories.add(category)

                # Add random tags
                random_tags = random.sample(tags, random.randint(1, 3))
                product.tags.set(random_tags)

                # Create variant
                variant = Variant.objects.create(
                    product=product,
                    name="Standard",
                    price=product_data["price"],
                    discount_price=product_data["discount"],
                )

                # Create stock for variant
                Stock.objects.create(
                    variant=variant,
                    quantity=random.randint(10, 100),
                    buying_price=product_data["price"]
                    * 0.6,  # Cost price is 60% of selling price
                )

                self.stdout.write(f"Created product: {product.name}")

        self.stdout.write(self.style.SUCCESS("Successfully created sample data!"))
