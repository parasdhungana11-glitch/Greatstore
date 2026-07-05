from django.core.management.base import BaseCommand
from store.models import Product

# Verified working Unsplash photo URLs for every product
FIXES = {
    # Clothes
    'classic-white-t-shirt':    'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600&q=80',
    'floral-summer-dress':      'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&q=80',
    'denim-jacket':             'https://images.unsplash.com/photo-1576871337622-98d48d1cf531?w=600&q=80',
    'sports-hoodie':            'https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=600&q=80',
    'slim-fit-chinos':          'https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&q=80',
    'silk-evening-blouse':      'https://images.unsplash.com/photo-1551163943-3f6a855d1153?w=600&q=80',

    # Watches
    'classic-silver-watch':         'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=80',
    'luxury-gold-watch':            'https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=600&q=80',
    'smart-watch-pro':              'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&q=80',
    'sports-chronograph':           'https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&q=80',
    'minimalist-rose-gold-watch':   'https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=600&q=80',

    # Shoes
    'running-sneakers':         'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80',
    'leather-oxford':           'https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=600&q=80',
    'high-heel-pumps':          'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&q=80',
    'casual-slip-on-loafers':   'https://images.unsplash.com/photo-1582588678413-dbf45f4823e9?w=600&q=80',

    # Bags — these were the broken ones
    'leather-handbag':  'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&q=80',
    'canvas-backpack':  'https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=600&q=80',
    'clutch-evening-bag': 'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=600&q=80',

    # Jewelry
    'gold-chain-necklace':      'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&q=80',
    'diamond-solitaire-ring':   'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=600&q=80',
    'silver-cuff-bracelet':     'https://images.unsplash.com/photo-1573408301185-9521e7d27cf4?w=600&q=80',

    # Sunglasses
    'aviator-sunglasses':       'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=600&q=80',
    'cat-eye-frames':           'https://images.unsplash.com/photo-1556306535-0f09a537f0a3?w=600&q=80',
    'oversized-square-shades':  'https://images.unsplash.com/photo-1508296695146-257a814070b4?w=600&q=80',

    # Hats
    'wool-fedora-hat':          'https://images.unsplash.com/photo-1521369909029-2afed882baee?w=600&q=80',
    'snapback-baseball-cap':    'https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=600&q=80',

    # Accessories
    'silk-printed-scarf':   'https://images.unsplash.com/photo-1601924994987-69e26d50dc26?w=600&q=80',
    'braided-leather-belt': 'https://images.unsplash.com/photo-1553062407-98d674fe1b79?w=600&q=80',
    'cashmere-gloves':      'https://images.unsplash.com/photo-1617791160536-598cf32026fb?w=600&q=80',
}


class Command(BaseCommand):
    help = 'Fix product image URLs to verified working ones'

    def handle(self, *args, **kwargs):
        fixed = 0
        for slug, url in FIXES.items():
            updated = Product.objects.filter(slug=slug).update(image_url=url)
            if updated:
                self.stdout.write(f'  Fixed: {slug}')
                fixed += updated
        self.stdout.write(self.style.SUCCESS(f'\nDone! Fixed {fixed} product images.'))
