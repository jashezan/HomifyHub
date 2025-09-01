from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from faker import Faker

from products.models import (
    Category,
    Tag,
    Product,
    ProductImage,
    Variant,
    Stock,
    Bundle,
    Review,
)
from users.models import Address
from blogs.models import BlogPost

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with realistic HomifyHub data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users",
            type=int,
            default=20,
            help="Number of users to create (default: 20)",
        )
        parser.add_argument(
            "--products",
            type=int,
            default=50,
            help="Number of products to create (default: 50)",
        )
        parser.add_argument(
            "--clear", action="store_true", help="Clear existing data before seeding"
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.clear_data()

        self.create_categories()
        self.create_tags()
        self.create_users(options["users"])
        self.create_products(options["products"])
        self.create_bundles()
        self.create_blog_posts()

        self.stdout.write(self.style.SUCCESS("Successfully seeded the database!"))

    def clear_data(self):
        """Clear existing data"""
        self.stdout.write("Clearing existing data...")

        # Clear in reverse order of dependencies
        Review.objects.all().delete()
        Bundle.objects.all().delete()
        Stock.objects.all().delete()
        Variant.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        BlogPost.objects.all().delete()
        Address.objects.all().delete()

        # Clear cart and wishlist data before users
        from carts.models import Cart, Wishlist, CartItem

        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Wishlist.objects.all().delete()

        User.objects.filter(is_superuser=False).delete()  # Keep superusers
        Tag.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Data cleared successfully!"))

    def create_categories(self):
        """Create home decor categories"""
        self.stdout.write("Creating categories...")

        # Main categories
        main_categories = [
            {
                "name": "Living Room",
                "description": "Furniture and decor for your living space",
                "subcategories": [
                    "Sofas & Couches",
                    "Coffee Tables",
                    "TV Stands",
                    "Armchairs",
                    "Ottomans",
                    "Side Tables",
                ],
            },
            {
                "name": "Bedroom",
                "description": "Create your perfect bedroom sanctuary",
                "subcategories": [
                    "Beds",
                    "Dressers",
                    "Nightstands",
                    "Wardrobes",
                    "Mirrors",
                    "Bedding",
                ],
            },
            {
                "name": "Dining Room",
                "description": "Dining furniture and accessories",
                "subcategories": [
                    "Dining Tables",
                    "Dining Chairs",
                    "Buffets",
                    "Bar Stools",
                    "China Cabinets",
                ],
            },
            {
                "name": "Office",
                "description": "Home office furniture and organization",
                "subcategories": [
                    "Desks",
                    "Office Chairs",
                    "Bookcases",
                    "File Cabinets",
                    "Desk Accessories",
                ],
            },
            {
                "name": "Kitchen",
                "description": "Kitchen furniture and storage solutions",
                "subcategories": [
                    "Kitchen Islands",
                    "Bar Carts",
                    "Storage Cabinets",
                    "Kitchen Stools",
                ],
            },
            {
                "name": "Outdoor",
                "description": "Outdoor furniture and garden decor",
                "subcategories": [
                    "Patio Sets",
                    "Garden Chairs",
                    "Outdoor Tables",
                    "Planters",
                    "Garden Decor",
                ],
            },
            {
                "name": "Lighting",
                "description": "Indoor and outdoor lighting solutions",
                "subcategories": [
                    "Ceiling Lights",
                    "Table Lamps",
                    "Floor Lamps",
                    "Wall Sconces",
                    "Outdoor Lighting",
                ],
            },
            {
                "name": "Decor",
                "description": "Home accessories and decorative items",
                "subcategories": [
                    "Wall Art",
                    "Vases",
                    "Candles",
                    "Throw Pillows",
                    "Rugs",
                    "Curtains",
                ],
            },
            {
                "name": "Storage",
                "description": "Organization and storage solutions",
                "subcategories": [
                    "Shelving Units",
                    "Storage Boxes",
                    "Baskets",
                    "Hooks & Hangers",
                    "Closet Organizers",
                ],
            },
        ]

        for main_cat_data in main_categories:
            main_cat, created = Category.objects.get_or_create(
                name=main_cat_data["name"],
                defaults={"description": main_cat_data["description"]},
            )

            # Create subcategories
            for sub_name in main_cat_data["subcategories"]:
                Category.objects.get_or_create(
                    name=sub_name,
                    parent=main_cat,
                    defaults={
                        "description": f'{sub_name} for your {main_cat_data["name"].lower()}'
                    },
                )

        self.stdout.write(f"Created {Category.objects.count()} categories")

    def create_tags(self):
        """Create product tags"""
        self.stdout.write("Creating tags...")

        tags = [
            "Modern",
            "Vintage",
            "Rustic",
            "Contemporary",
            "Traditional",
            "Minimalist",
            "Industrial",
            "Scandinavian",
            "Bohemian",
            "Mid-Century",
            "Eco-Friendly",
            "Handmade",
            "Premium",
            "Luxury",
            "Budget-Friendly",
            "Compact",
            "Space-Saving",
            "Multifunctional",
            "Adjustable",
            "Portable",
            "Wood",
            "Metal",
            "Glass",
            "Fabric",
            "Leather",
            "Plastic",
            "Bamboo",
            "Black",
            "White",
            "Brown",
            "Gray",
            "Blue",
            "Green",
            "Red",
            "Gold",
            "Sale",
            "New Arrival",
            "Best Seller",
            "Featured",
            "Limited Edition",
            "Indoor",
            "Outdoor",
            "Waterproof",
            "UV-Resistant",
            "Weatherproof",
        ]

        for tag_name in tags:
            Tag.objects.get_or_create(name=tag_name)

        self.stdout.write(f"Created {Tag.objects.count()} tags")

    def create_users(self, count):
        """Create users (customers and sellers)"""
        self.stdout.write(f"Creating {count} users...")

        for i in range(count):
            # 80% customers, 20% sellers
            is_seller = random.random() < 0.2

            first_name = fake.first_name()
            last_name = fake.last_name()
            username = (
                f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}"
            )
            email = f"{username}@{fake.domain_name()}"

            user = User.objects.create_user(
                username=username,
                email=email,
                password="password123",
                first_name=first_name,
                last_name=last_name,
                phone=fake.phone_number()[:15] if random.random() < 0.7 else "",
                is_seller=is_seller,
                is_active=True,
            )

            # Create 1-3 addresses for each user
            for _ in range(random.randint(1, 3)):
                is_default = _ == 0  # First address is default
                Address.objects.create(
                    user=user,
                    name=random.choice(
                        ["Home", "Work", "Office", "Apartment", "House"]
                    ),
                    street=fake.street_address(),
                    city=fake.city(),
                    state=fake.state(),
                    postal_code=fake.postcode(),
                    country=fake.country(),
                    is_default=is_default,
                )

        self.stdout.write(
            f"Created {User.objects.filter(is_superuser=False).count()} users"
        )

    def create_products(self, count):
        """Create products with variants, images, and stock"""
        self.stdout.write(f"Creating {count} products...")

        # Product name templates for different categories
        product_templates = {
            "Sofas & Couches": [
                "Modern Sectional Sofa",
                "Vintage Leather Couch",
                "Contemporary Loveseat",
                "Scandinavian Fabric Sofa",
                "Mid-Century Velvet Couch",
                "Industrial Steel Sofa",
            ],
            "Coffee Tables": [
                "Glass Top Coffee Table",
                "Wooden Round Coffee Table",
                "Industrial Metal Table",
                "Marble Coffee Table",
                "Storage Ottoman Table",
                "Live Edge Wood Table",
            ],
            "Beds": [
                "Platform Bed Frame",
                "Upholstered Headboard Bed",
                "Storage Bed",
                "Canopy Bed",
                "Sleigh Bed",
                "Murphy Bed",
            ],
            "Dining Tables": [
                "Extendable Dining Table",
                "Round Pedestal Table",
                "Farmhouse Dining Table",
                "Glass Dining Table",
                "Counter Height Table",
                "Outdoor Dining Table",
            ],
            "Table Lamps": [
                "Ceramic Table Lamp",
                "Brass Desk Lamp",
                "Fabric Shade Lamp",
                "Crystal Table Lamp",
                "Industrial Pipe Lamp",
                "Touch Control Lamp",
            ],
            "Wall Art": [
                "Abstract Canvas Print",
                "Vintage Poster Set",
                "Metal Wall Sculpture",
                "Framed Photography",
                "Wooden Wall Art",
                "Gallery Wall Collection",
            ],
        }

        categories = list(
            Category.objects.filter(parent__isnull=False)
        )  # Get subcategories
        tags = list(Tag.objects.all())

        for i in range(count):
            # Choose random category
            category = random.choice(categories)

            # Get product name based on category
            if category.name in product_templates:
                base_name = random.choice(product_templates[category.name])
            else:
                base_name = f"{fake.word().title()} {category.name[:-1]}"  # Remove 's' from plural

            # Add descriptive words
            descriptors = [
                "Premium",
                "Luxury",
                "Compact",
                "Designer",
                "Classic",
                "Elegant",
            ]
            if random.random() < 0.3:
                base_name = f"{random.choice(descriptors)} {base_name}"

            # Ensure unique product name
            counter = 1
            original_name = base_name
            while Product.objects.filter(name=base_name).exists():
                base_name = f"{original_name} {counter}"
                counter += 1

            # Create product
            product = Product.objects.create(
                name=base_name,
                description=self.generate_product_description(base_name, category),
                specifications=self.generate_specifications(category),
                is_customizable=random.random() < 0.3,
                customization_options=(
                    self.generate_customization_options()
                    if random.random() < 0.3
                    else {}
                ),
            )

            # Add categories and tags
            product.categories.add(category)
            if category.parent:
                product.categories.add(category.parent)

            # Add 2-5 random tags
            product_tags = random.sample(tags, random.randint(2, 5))
            product.tags.set(product_tags)

            # Create product images (2-5 images per product)
            self.create_product_images(product, random.randint(2, 5))

            # Create variants (1-4 variants per product)
            self.create_variants(product, random.randint(1, 4))

            # Add reviews (0-10 reviews per product)
            self.create_reviews(product, random.randint(0, 10))

        self.stdout.write(f"Created {Product.objects.count()} products")

    def generate_product_description(self, name, category):
        """Generate realistic product description"""
        descriptions = [
            f"Transform your {category.parent.name.lower() if category.parent else 'space'} with this beautiful {name.lower()}. ",
            f"Crafted with attention to detail, this {name.lower()} combines style and functionality. ",
            f"Add a touch of elegance to your home with this stunning {name.lower()}. ",
        ]

        features = [
            "Made from high-quality materials for durability and longevity.",
            "Easy to assemble with included hardware and instructions.",
            "Perfect for modern and contemporary home decor styles.",
            "Available in multiple colors and finishes to match your decor.",
            "Designed for everyday use and built to last.",
            "Eco-friendly materials and sustainable manufacturing process.",
            "Professional design that fits seamlessly into any room.",
            "Compact size perfect for small spaces without compromising style.",
        ]

        description = random.choice(descriptions)
        description += " ".join(random.sample(features, random.randint(2, 4)))

        return description

    def generate_specifications(self, category):
        """Generate product specifications based on category"""
        specs = {}

        # Common specs
        materials = [
            "Wood",
            "Metal",
            "Glass",
            "Fabric",
            "Leather",
            "Plastic",
            "Bamboo",
            "Marble",
        ]
        specs["Material"] = random.choice(materials)

        colors = [
            "Black",
            "White",
            "Brown",
            "Gray",
            "Navy",
            "Beige",
            "Natural",
            "Walnut",
        ]
        specs["Color"] = random.choice(colors)

        # Category-specific specs
        if "Table" in category.name or "Desk" in category.name:
            specs["Dimensions"] = (
                f'{random.randint(40, 80)}" W x {random.randint(20, 40)}" D x {random.randint(28, 32)}" H'
            )
            specs["Weight"] = f"{random.randint(30, 100)} lbs"
        elif "Chair" in category.name or "Stool" in category.name:
            specs["Dimensions"] = (
                f'{random.randint(18, 30)}" W x {random.randint(18, 30)}" D x {random.randint(30, 45)}" H'
            )
            specs["Weight Capacity"] = f"{random.randint(200, 350)} lbs"
        elif "Sofa" in category.name or "Couch" in category.name:
            specs["Dimensions"] = (
                f'{random.randint(60, 100)}" W x {random.randint(30, 40)}" D x {random.randint(30, 40)}" H'
            )
            specs["Seating Capacity"] = f"{random.randint(2, 4)} people"
        elif "Bed" in category.name:
            sizes = ["Twin", "Full", "Queen", "King", "California King"]
            specs["Size"] = random.choice(sizes)
            specs["Headboard Height"] = f'{random.randint(40, 60)}"'
        elif "Lamp" in category.name:
            specs["Bulb Type"] = random.choice(["LED", "CFL", "Incandescent"])
            specs["Wattage"] = f"{random.randint(40, 100)}W"
            specs["Height"] = f'{random.randint(15, 30)}"'

        # Assembly
        specs["Assembly Required"] = random.choice(["Yes", "No", "Minimal"])

        # Warranty
        specs["Warranty"] = (
            f"{random.randint(1, 5)} Year{'s' if random.randint(1, 5) > 1 else ''}"
        )

        return specs

    def generate_customization_options(self):
        """Generate customization options"""
        options = {}

        if random.random() < 0.7:
            colors = ["Black", "White", "Brown", "Gray", "Navy", "Red", "Blue", "Green"]
            options["Colors"] = random.sample(colors, random.randint(2, 4))

        if random.random() < 0.5:
            sizes = ["Small", "Medium", "Large", "Extra Large"]
            options["Sizes"] = random.sample(sizes, random.randint(2, 3))

        if random.random() < 0.3:
            materials = ["Wood", "Metal", "Glass", "Fabric"]
            options["Materials"] = random.sample(materials, random.randint(2, 3))

        if random.random() < 0.2:
            options["Engraving"] = True

        return options

    def create_product_images(self, product, count):
        """Create product images with placeholder URLs"""
        for i in range(count):
            # Use placeholder image service
            width = random.choice([400, 500, 600])
            height = random.choice([300, 400, 500])
            image_url = (
                f"https://picsum.photos/{width}/{height}?random={product.id}_{i}"
            )

            ProductImage.objects.create(
                product=product,
                image_url=image_url,
                is_primary=(i == 0),  # First image is primary
            )

    def create_variants(self, product, count):
        """Create product variants with different attributes"""
        colors = ["Black", "White", "Brown", "Gray", "Navy", "Beige"]
        sizes = ["Small", "Medium", "Large"]
        materials = ["Wood", "Metal", "Fabric", "Leather"]

        for i in range(count):
            if count == 1:
                variant_name = "Standard"
                attributes = {}
            else:
                attributes = {}
                variant_parts = []

                if random.random() < 0.8:  # 80% chance of color variation
                    color = random.choice(colors)
                    attributes["color"] = color
                    variant_parts.append(color)

                if random.random() < 0.5:  # 50% chance of size variation
                    size = random.choice(sizes)
                    attributes["size"] = size
                    variant_parts.append(size)

                if random.random() < 0.3:  # 30% chance of material variation
                    material = random.choice(materials)
                    attributes["material"] = material
                    variant_parts.append(material)

                if variant_parts:
                    variant_name = " - ".join(variant_parts)
                else:
                    variant_name = f"Variant {i+1}"

            # Make sure variant name is unique for this product
            counter = 1
            original_name = variant_name
            while Variant.objects.filter(product=product, name=variant_name).exists():
                variant_name = f"{original_name} ({counter})"
                counter += 1

            # Generate realistic pricing
            base_price = Decimal(str(random.randint(50, 2000)))
            discount_price = None

            # 30% chance of discount
            if random.random() < 0.3:
                discount_percentage = random.randint(10, 40)
                discount_price = base_price * Decimal(
                    str(1 - discount_percentage / 100)
                )
                discount_price = discount_price.quantize(Decimal("0.01"))

            variant = Variant.objects.create(
                product=product,
                name=variant_name,
                attributes=attributes,
                price=base_price,
                discount_price=discount_price,
            )

            # Create stock for this variant (1-3 stock entries with different buying prices)
            for _ in range(random.randint(1, 3)):
                Stock.objects.create(
                    variant=variant,
                    quantity=random.randint(5, 50),
                    buying_price=base_price
                    * Decimal(str(random.uniform(0.5, 0.8))),  # 50-80% of selling price
                )

    def create_reviews(self, product, count):
        """Create product reviews"""
        users = list(User.objects.filter(is_seller=False))
        if not users or count == 0:
            return

        review_comments = [
            "Great quality product! Very satisfied with my purchase.",
            "Exactly as described. Fast shipping and well packaged.",
            "Beautiful design and excellent craftsmanship.",
            "Perfect for my space. Highly recommend!",
            "Good value for money. Would buy again.",
            "Easy to assemble and looks amazing in my room.",
            "Quality materials and sturdy construction.",
            "Love the modern design. Fits perfectly with my decor.",
            "Excellent customer service and fast delivery.",
            "Outstanding product quality. Exceeded my expectations.",
            "Very comfortable and stylish. Great addition to my home.",
            "Professional packaging and excellent build quality.",
            "Perfect size and color. Exactly what I was looking for.",
            "Impressive quality for the price point.",
            "Beautiful finish and attention to detail.",
        ]

        negative_comments = [
            "Not as pictured. Quality could be better.",
            "Assembly was more difficult than expected.",
            "Smaller than I thought it would be.",
            "Color was slightly different from the photos.",
            "Good product but delivery took longer than expected.",
        ]

        selected_users = random.sample(users, min(count, len(users)))

        for user in selected_users:
            # 85% chance of positive review (4-5 stars)
            if random.random() < 0.85:
                rating = random.randint(4, 5)
                comment = random.choice(review_comments)
            else:
                rating = random.randint(2, 3)
                comment = random.choice(negative_comments)

            Review.objects.create(
                product=product,
                user=user,
                rating=rating,
                comment=comment,
                created_at=fake.date_time_between(
                    start_date="-1y",
                    end_date="now",
                    tzinfo=timezone.get_current_timezone(),
                ),
            )

    def create_bundles(self):
        """Create product bundles"""
        self.stdout.write("Creating product bundles...")

        products = list(Product.objects.all())
        if len(products) < 6:
            return

        bundle_ideas = [
            {
                "name": "Complete Living Room Set",
                "description": "Transform your living room with this complete furniture set including sofa, coffee table, and accent pieces.",
                "categories": ["Sofas & Couches", "Coffee Tables", "Side Tables"],
            },
            {
                "name": "Bedroom Essentials Bundle",
                "description": "Everything you need for a perfect bedroom setup including bed, nightstands, and dresser.",
                "categories": ["Beds", "Nightstands", "Dressers"],
            },
            {
                "name": "Home Office Starter Kit",
                "description": "Get productive with this complete home office bundle featuring desk, chair, and storage solutions.",
                "categories": ["Desks", "Office Chairs", "Bookcases"],
            },
            {
                "name": "Dining Room Collection",
                "description": "Host memorable dinners with this elegant dining room set including table and chairs.",
                "categories": ["Dining Tables", "Dining Chairs"],
            },
            {
                "name": "Lighting Package",
                "description": "Illuminate your home with this carefully curated lighting collection for every room.",
                "categories": ["Table Lamps", "Floor Lamps", "Ceiling Lights"],
            },
        ]

        for bundle_data in bundle_ideas:
            # Check if bundle already exists
            if Bundle.objects.filter(name=bundle_data["name"]).exists():
                continue

            # Find products matching the bundle categories
            bundle_products = []
            for cat_name in bundle_data["categories"]:
                category_products = Product.objects.filter(categories__name=cat_name)
                if category_products.exists():
                    bundle_products.append(random.choice(category_products))

            if len(bundle_products) >= 2:
                # Calculate bundle price (sum of individual prices with 15-25% discount)
                total_price = sum(
                    p.variants.first().price
                    for p in bundle_products
                    if p.variants.exists()
                )
                if total_price > 0:
                    discount_percentage = random.randint(15, 25)
                    bundle_price = total_price
                    discount_price = total_price * Decimal(
                        str(1 - discount_percentage / 100)
                    )
                    discount_price = discount_price.quantize(Decimal("0.01"))

                    bundle = Bundle.objects.create(
                        name=bundle_data["name"],
                        description=bundle_data["description"],
                        bundle_price=bundle_price,
                        discount_price=discount_price,
                    )

                    bundle.products.set(bundle_products)

        self.stdout.write(f"Created {Bundle.objects.count()} bundles")

    def create_blog_posts(self):
        """Create blog posts"""
        self.stdout.write("Creating blog posts...")

        # Get some sellers as authors
        authors = list(User.objects.filter(is_seller=True))
        if not authors:
            return

        blog_topics = [
            {
                "title": "10 Modern Living Room Design Ideas for 2025",
                "content": "Discover the latest trends in modern living room design. From minimalist furniture to bold accent pieces, we explore how to create a contemporary space that reflects your personal style.",
                "excerpt": "Explore the hottest living room design trends for 2025 and learn how to create a modern space that's both stylish and functional.",
            },
            {
                "title": "Small Space, Big Style: Maximizing Your Apartment",
                "content": "Living in a small space doesn't mean sacrificing style. Learn practical tips and tricks for making the most of your apartment with clever furniture choices and space-saving solutions.",
                "excerpt": "Transform your small apartment into a stylish haven with these expert tips for maximizing space and style.",
            },
            {
                "title": "Sustainable Home Decor: Eco-Friendly Design Choices",
                "content": "Make environmentally conscious choices for your home decor. Discover sustainable materials, eco-friendly furniture options, and green design principles that benefit both your home and the planet.",
                "excerpt": "Learn how to create a beautiful home while making environmentally responsible choices with sustainable decor options.",
            },
            {
                "title": "The Complete Guide to Home Office Setup",
                "content": "Working from home requires a dedicated workspace that promotes productivity and comfort. Our comprehensive guide covers everything from desk selection to lighting and organization.",
                "excerpt": "Create the perfect home office with our expert guide covering furniture, lighting, and organization essentials.",
            },
            {
                "title": "Seasonal Decor: Refreshing Your Home Year-Round",
                "content": "Keep your home feeling fresh and current with seasonal decor updates. Learn how to incorporate seasonal elements without major renovations or expensive purchases.",
                "excerpt": "Discover simple ways to update your home decor with the seasons using affordable and stylish seasonal elements.",
            },
            {
                "title": "Color Psychology in Interior Design",
                "content": "Colors have a profound impact on mood and atmosphere. Understand how different colors affect your emotions and learn to use color psychology in your interior design choices.",
                "excerpt": "Harness the power of color psychology to create spaces that promote the mood and atmosphere you desire.",
            },
            {
                "title": "Mixing Textures: Adding Depth to Your Decor",
                "content": "Texture plays a crucial role in creating visual interest and depth in interior design. Learn how to successfully mix different textures to create a rich, layered look.",
                "excerpt": "Master the art of mixing textures to add visual interest and sophistication to any room in your home.",
            },
            {
                "title": "Budget-Friendly Home Makeover Ideas",
                "content": "Transform your space without breaking the bank. Discover creative and affordable ways to refresh your home decor using DIY projects and smart shopping strategies.",
                "excerpt": "Give your home a fresh new look on a budget with these creative and affordable makeover ideas.",
            },
        ]

        for i, blog_data in enumerate(blog_topics):
            # Check if blog post with this title already exists
            title = blog_data["title"]
            counter = 1
            original_title = title
            while BlogPost.objects.filter(title=title).exists():
                title = f"{original_title} {counter}"
                counter += 1

            author = random.choice(authors)
            is_published = random.random() < 0.8  # 80% of posts are published

            BlogPost.objects.create(
                title=title,
                author=author,
                content=blog_data["content"]
                + "\n\n"
                + fake.text(max_nb_chars=1000),  # Add more content
                excerpt=blog_data["excerpt"],
                is_published=is_published,
                created_at=fake.date_time_between(
                    start_date="-6m",
                    end_date="now",
                    tzinfo=timezone.get_current_timezone(),
                ),
                updated_at=fake.date_time_between(
                    start_date="-3m",
                    end_date="now",
                    tzinfo=timezone.get_current_timezone(),
                ),
            )

        self.stdout.write(f"Created {BlogPost.objects.count()} blog posts")
