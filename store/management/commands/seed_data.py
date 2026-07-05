from django.core.management.base import BaseCommand
from django.utils.text import slugify
from store.models import Category, Product

CATEGORIES = [
    {'name': 'Clothes',    'icon': '👕', 'description': 'Men and women fashion clothing'},
    {'name': 'Watches',    'icon': '⌚', 'description': 'Luxury and sport timepieces'},
    {'name': 'Shoes',      'icon': '👟', 'description': 'Sneakers, heels, boots and more'},
    {'name': 'Bags',       'icon': '👜', 'description': 'Handbags, backpacks and wallets'},
    {'name': 'Jewelry',    'icon': '💎', 'description': 'Rings, necklaces and bracelets'},
    {'name': 'Sunglasses', 'icon': '🕶️', 'description': 'Designer and sport eyewear'},
    {'name': 'Hats',       'icon': '🧢', 'description': 'Caps, fedoras and beanies'},
    {'name': 'Accessories','icon': '🎀', 'description': 'Scarves, belts and more'},
]

# Free images from picsum.photos (seeded = consistent) and Unsplash
PRODUCTS = [
    # ── CLOTHES ────────────────────────────────────────────────────────────────
    {
        'name': 'Classic White T-Shirt',
        'category': 'Clothes', 'price': 29.99, 'original_price': 49.99,
        'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80',
        'description': 'Soft cotton essential white tee, perfect for any occasion.',
        'featured': True, 'rating': 4.6,
    },
    {
        'name': 'Floral Summer Dress',
        'category': 'Clothes', 'price': 79.99, 'original_price': 119.99,
        'image_url': 'https://images.unsplash.com/photo-1572804013427-4d7ca7268217?w=600&q=80',
        'description': 'Light floral print dress ideal for sunny days.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Denim Jacket',
        'category': 'Clothes', 'price': 99.99, 'original_price': None,
        'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&q=80',
        'description': 'Versatile denim jacket for a timeless casual look.',
        'featured': False, 'rating': 4.4,
    },
    {
        'name': 'Sports Hoodie',
        'category': 'Clothes', 'price': 59.99, 'original_price': 89.99,
        'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&q=80',
        'description': 'Comfortable fleece hoodie for workouts and casual wear.',
        'featured': True, 'rating': 4.7,
    },
    {
        'name': 'Slim Fit Chinos',
        'category': 'Clothes', 'price': 69.99, 'original_price': 99.99,
        'image_url': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600&q=80',
        'description': 'Smart slim-fit chinos available in multiple colours.',
        'featured': False, 'rating': 4.3,
    },
    {
        'name': 'Silk Evening Blouse',
        'category': 'Clothes', 'price': 89.99, 'original_price': 129.99,
        'image_url': 'https://images.unsplash.com/photo-1562572159-4efc207f5aff?w=600&q=80',
        'description': 'Elegant silk blouse for formal and evening occasions.',
        'featured': True, 'rating': 4.9,
    },

    # ── WATCHES ────────────────────────────────────────────────────────────────
    {
        'name': 'Classic Silver Watch',
        'category': 'Watches', 'price': 299.99, 'original_price': 399.99,
        'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80',
        'description': 'Swiss-inspired silver case with sapphire crystal glass.',
        'featured': True, 'rating': 4.9,
    },
    {
        'name': 'Luxury Gold Watch',
        'category': 'Watches', 'price': 599.99, 'original_price': 799.99,
        'image_url': 'https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=600&q=80',
        'description': 'Premium gold-plated watch with leather strap.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Smart Watch Pro',
        'category': 'Watches', 'price': 399.99, 'original_price': None,
        'image_url': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80',
        'description': 'Advanced smart watch with health tracking and GPS.',
        'featured': True, 'rating': 4.7,
    },
    {
        'name': 'Sports Chronograph',
        'category': 'Watches', 'price': 149.99, 'original_price': 199.99,
        'image_url': 'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80',
        'description': 'Durable chronograph with silicone band for active lifestyles.',
        'featured': False, 'rating': 4.4,
    },
    {
        'name': 'Minimalist Rose Gold Watch',
        'category': 'Watches', 'price': 219.99, 'original_price': 279.99,
        'image_url': 'https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=600&q=80',
        'description': 'Ultra-thin minimalist dial in elegant rose gold finish.',
        'featured': False, 'rating': 4.6,
    },

    # ── SHOES ──────────────────────────────────────────────────────────────────
    {
        'name': 'Running Sneakers',
        'category': 'Shoes', 'price': 89.99, 'original_price': 119.99,
        'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80',
        'description': 'Lightweight and breathable sneakers for daily runs.',
        'featured': True, 'rating': 4.6,
    },
    {
        'name': 'Leather Oxford',
        'category': 'Shoes', 'price': 149.99, 'original_price': None,
        'image_url': 'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&q=80',
        'description': 'Hand-stitched full-grain leather Oxford shoes.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'High Heel Pumps',
        'category': 'Shoes', 'price': 109.99, 'original_price': 159.99,
        'image_url': 'https://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=600&q=80',
        'description': 'Classic stiletto pumps in genuine suede.',
        'featured': False, 'rating': 4.3,
    },
    {
        'name': 'Casual Slip-On Loafers',
        'category': 'Shoes', 'price': 69.99, 'original_price': 99.99,
        'image_url': 'https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=600&q=80',
        'description': 'Effortless slip-on loafers with memory foam insoles.',
        'featured': False, 'rating': 4.4,
    },

    # ── BAGS ───────────────────────────────────────────────────────────────────
    {
        'name': 'Leather Handbag',
        'category': 'Bags', 'price': 129.99, 'original_price': 189.99,
        'image_url': 'https://images.unsplash.com/photo-1548036161-f5b1cfc3ec89?w=600&q=80',
        'description': 'Genuine leather structured handbag with gold hardware.',
        'featured': True, 'rating': 4.7,
    },
    {
        'name': 'Canvas Backpack',
        'category': 'Bags', 'price': 79.99, 'original_price': 109.99,
        'image_url': 'https://images.unsplash.com/photo-1553062407-98d674fe1b79?w=600&q=80',
        'description': 'Durable canvas backpack with laptop compartment.',
        'featured': True, 'rating': 4.5,
    },
    {
        'name': 'Clutch Evening Bag',
        'category': 'Bags', 'price': 59.99, 'original_price': 79.99,
        'image_url': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=600&q=80',
        'description': 'Compact beaded clutch perfect for evenings out.',
        'featured': False, 'rating': 4.2,
    },

    # ── JEWELRY ────────────────────────────────────────────────────────────────
    {
        'name': 'Gold Chain Necklace',
        'category': 'Jewelry', 'price': 199.99, 'original_price': 249.99,
        'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600&q=80',
        'description': '18k gold-plated rope chain necklace, 45 cm.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Diamond Solitaire Ring',
        'category': 'Jewelry', 'price': 499.99, 'original_price': 699.99,
        'image_url': 'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600&q=80',
        'description': 'Brilliant-cut diamond set in 14k white gold band.',
        'featured': True, 'rating': 4.9,
    },
    {
        'name': 'Silver Cuff Bracelet',
        'category': 'Jewelry', 'price': 89.99, 'original_price': 119.99,
        'image_url': 'https://images.unsplash.com/photo-1611652022419-a9419f74343d?w=600&q=80',
        'description': 'Sterling silver adjustable cuff bracelet with engravings.',
        'featured': False, 'rating': 4.4,
    },

    # ── SUNGLASSES ─────────────────────────────────────────────────────────────
    {
        'name': 'Aviator Sunglasses',
        'category': 'Sunglasses', 'price': 79.99, 'original_price': 109.99,
        'image_url': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&q=80',
        'description': 'Classic metal-frame aviators with UV400 polarised lenses.',
        'featured': True, 'rating': 4.6,
    },
    {
        'name': 'Cat Eye Frames',
        'category': 'Sunglasses', 'price': 69.99, 'original_price': 89.99,
        'image_url': 'https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=600&q=80',
        'description': 'Retro cat-eye frames in tortoiseshell acetate.',
        'featured': False, 'rating': 4.3,
    },
    {
        'name': 'Oversized Square Shades',
        'category': 'Sunglasses', 'price': 59.99, 'original_price': None,
        'image_url': 'https://images.unsplash.com/photo-1473496169904-658ba7574b0d?w=600&q=80',
        'description': 'Bold oversized square frames for a glamorous look.',
        'featured': False, 'rating': 4.5,
    },

    # ── HATS ───────────────────────────────────────────────────────────────────
    {
        'name': 'Wool Fedora Hat',
        'category': 'Hats', 'price': 49.99, 'original_price': 69.99,
        'image_url': 'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=600&q=80',
        'description': 'Classic wide-brim fedora crafted from 100% wool.',
        'featured': True, 'rating': 4.6,
    },
    {
        'name': 'Snapback Baseball Cap',
        'category': 'Hats', 'price': 29.99, 'original_price': 39.99,
        'image_url': 'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&q=80',
        'description': 'Adjustable snapback cap in embroidered cotton twill.',
        'featured': False, 'rating': 4.2,
    },

    # ── ACCESSORIES ────────────────────────────────────────────────────────────
    {
        'name': 'Silk Printed Scarf',
        'category': 'Accessories', 'price': 39.99, 'original_price': 59.99,
        'image_url': 'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&q=80',
        'description': 'Luxurious 100% silk scarf with artistic print.',
        'featured': True, 'rating': 4.5,
    },
    {
        'name': 'Braided Leather Belt',
        'category': 'Accessories', 'price': 34.99, 'original_price': 49.99,
        'image_url': 'https://images.unsplash.com/photo-1624806992066-5ffcf7ca186b?w=600&q=80',
        'description': 'Hand-braided genuine leather belt with antique buckle.',
        'featured': False, 'rating': 4.3,
    },
    {
        'name': 'Cashmere Gloves',
        'category': 'Accessories', 'price': 44.99, 'original_price': 64.99,
        'image_url': 'https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=600&q=80',
        'description': 'Soft cashmere gloves with touchscreen-compatible fingertips.',
        'featured': False, 'rating': 4.7,
    },

    # ── MORE WATCHES (total → 9) ───────────────────────────────────────────────
    {
        'name': 'Blue Dial Automatic Watch',
        'category': 'Watches', 'price': 329.99, 'original_price': 449.99,
        'image_url': 'https://images.unsplash.com/photo-1526045612212-70caf35c14df?w=600&q=80',
        'description': 'Japanese automatic movement with a stunning ocean-blue dial and brushed steel case.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Skeleton Mechanical Watch',
        'category': 'Watches', 'price': 549.99, 'original_price': 749.99,
        'image_url': 'https://images.unsplash.com/photo-1588345921523-c2dcdb7f1dcd?w=600&q=80',
        'description': 'Open-heart skeleton dial revealing intricate mechanical movement inside.',
        'featured': True, 'rating': 4.9,
    },
    {
        'name': 'Titanium Sport Watch',
        'category': 'Watches', 'price': 459.99, 'original_price': 599.99,
        'image_url': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=600&q=80',
        'description': 'Lightweight titanium sport watch with solar charging and 100m water resistance.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Ladies Rose Crystal Watch',
        'category': 'Watches', 'price': 199.99, 'original_price': 269.99,
        'image_url': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=600&q=80',
        'description': 'Elegant ladies watch with crystal-embellished bezel and rose-gold mesh bracelet.',
        'featured': True, 'rating': 4.7,
    },

    # ── MORE FEATURED PRODUCTS (5 new categories) ─────────────────────────────
    {
        'name': 'Premium Leather Jacket',
        'category': 'Clothes', 'price': 249.99, 'original_price': 349.99,
        'image_url': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=80',
        'description': 'Genuine lambskin leather jacket with quilted lining and polished silver zips.',
        'featured': True, 'rating': 4.9,
    },
    {
        'name': 'Velvet Cocktail Dress',
        'category': 'Clothes', 'price': 139.99, 'original_price': 199.99,
        'image_url': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80',
        'description': 'Fitted velvet midi dress with sweetheart neckline — perfect for special evenings.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Chunky Platform Sneakers',
        'category': 'Shoes', 'price': 129.99, 'original_price': 179.99,
        'image_url': 'https://images.unsplash.com/photo-1605348532760-6753d2c43329?w=600&q=80',
        'description': 'Trendy chunky platform sneakers with thick rubber outsole and padded ankle collar.',
        'featured': True, 'rating': 4.5,
    },
    {
        'name': 'Quilted Chain Shoulder Bag',
        'category': 'Bags', 'price': 179.99, 'original_price': 249.99,
        'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&q=80',
        'description': 'Classic diamond-quilted bag with gold chain strap and turn-lock closure.',
        'featured': True, 'rating': 4.8,
    },
    {
        'name': 'Pearl Drop Earrings',
        'category': 'Jewelry', 'price': 69.99, 'original_price': 99.99,
        'image_url': 'https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=600&q=80',
        'description': 'Freshwater pearl drop earrings with sterling silver hooks, timeless and elegant.',
        'featured': True, 'rating': 4.7,
    },

    # ── NEW ARRIVALS (placed last = newest timestamps = appear in new arrivals) ─
    {
        'name': 'Linen Wide-Leg Trousers',
        'category': 'Clothes', 'price': 74.99, 'original_price': 109.99,
        'image_url': 'https://images.unsplash.com/photo-1509631179647-0177331693ae?w=600&q=80',
        'description': 'Breathable linen trousers in a relaxed wide-leg silhouette, ideal for summer.',
        'featured': False, 'rating': 4.4,
    },
    {
        'name': 'Suede Chelsea Boots',
        'category': 'Shoes', 'price': 169.99, 'original_price': 219.99,
        'image_url': 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&q=80',
        'description': 'Genuine suede chelsea boots with elastic gussets and a sturdy block heel.',
        'featured': False, 'rating': 4.6,
    },
    {
        'name': 'Woven Raffia Beach Tote',
        'category': 'Bags', 'price': 59.99, 'original_price': 84.99,
        'image_url': 'https://images.unsplash.com/photo-1590739293931-a4f79cf92a55?w=600&q=80',
        'description': 'Handwoven natural raffia tote with leather handles — your perfect beach companion.',
        'featured': False, 'rating': 4.3,
    },
    {
        'name': 'Round Tortoise Sunglasses',
        'category': 'Sunglasses', 'price': 84.99, 'original_price': 114.99,
        'image_url': 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=80',
        'description': 'Classic round tortoiseshell acetate frames with gradient UV400 polarised lenses.',
        'featured': False, 'rating': 4.5,
    },
    {
        'name': 'Graphic Oversized Hoodie',
        'category': 'Clothes', 'price': 64.99, 'original_price': 89.99,
        'image_url': 'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&q=80',
        'description': 'Heavyweight fleece hoodie in an oversized streetwear fit with bold graphic print.',
        'featured': False, 'rating': 4.4,
    },
    {
        'name': 'Slim RFID Leather Wallet',
        'category': 'Accessories', 'price': 49.99, 'original_price': 69.99,
        'image_url': 'https://images.unsplash.com/photo-1548036161-f5b1cfc3ec89?w=600&q=80',
        'description': 'Ultra-slim bi-fold wallet in top-grain leather with built-in RFID-blocking lining.',
        'featured': False, 'rating': 4.6,
    },
    {
        'name': 'Ribbed Knit Beanie',
        'category': 'Hats', 'price': 24.99, 'original_price': 34.99,
        'image_url': 'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=600&q=80',
        'description': 'Soft ribbed-knit beanie in merino wool blend — warm and stylish for cold days.',
        'featured': False, 'rating': 4.3,
    },
    {
        'name': 'Layered Gold Chain Necklace Set',
        'category': 'Jewelry', 'price': 79.99, 'original_price': 109.99,
        'image_url': 'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=600&q=80',
        'description': 'Set of three delicate 18k gold-plated chains designed to be worn layered together.',
        'featured': False, 'rating': 4.5,
    },
]


class Command(BaseCommand):
    help = 'Seed the database with categories and products'

    def handle(self, *args, **kwargs):
        self.stdout.write('Clearing old data...')
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write('Creating categories...')
        cat_map = {}
        for c in CATEGORIES:
            cat = Category.objects.create(
                name=c['name'],
                slug=slugify(c['name']),
                icon=c['icon'],
                description=c['description'],
            )
            cat_map[c['name']] = cat
            self.stdout.write(f'  OK {c["name"]}')

        self.stdout.write('Creating products...')
        for p in PRODUCTS:
            product = Product.objects.create(
                name=p['name'],
                slug=slugify(p['name']),
                category=cat_map[p['category']],
                description=p['description'],
                price=p['price'],
                original_price=p.get('original_price'),
                image_url=p['image_url'],
                is_featured=p.get('featured', False),
                rating=p.get('rating', 4.5),
                stock=50,
            )
            self.stdout.write(f'  + {product.name} ${product.price}')

        self.stdout.write(self.style.SUCCESS(f'\nDone! {Category.objects.count()} categories, {Product.objects.count()} products created.'))
