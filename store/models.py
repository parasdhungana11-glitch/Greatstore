from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='🛍️')
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    SIZES = [('XS','XS'), ('S','S'), ('M','M'), ('L','L'), ('XL','XL'), ('XXL','XXL'), ('ONE','One Size')]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField(default='')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=500)
    daraz_url = models.URLField(max_length=600, blank=True, help_text='Direct Daraz product URL (optional). If blank, a search link is auto-generated.')
    stock = models.IntegerField(default=50)
    is_featured = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def price_npr(self):
        return int(self.price * 133)

    @property
    def original_price_npr(self):
        if self.original_price:
            return int(self.original_price * 133)
        return None

    @property
    def discount_percent(self):
        if self.original_price and self.original_price > self.price:
            return int((1 - self.price / self.original_price) * 100)
        return 0

    @property
    def daraz_link(self):
        if self.daraz_url:
            return self.daraz_url
        from urllib.parse import quote_plus
        return f'https://www.daraz.com.np/catalog/?q={quote_plus(self.name)}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum(item.subtotal for item in self.items.select_related('product').all())

    def item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True, default='M')

    @property
    def subtotal(self):
        return self.product.price * self.quantity


class Order(models.Model):
    STATUS = [('pending','Pending'), ('processing','Processing'), ('shipped','Shipped'), ('delivered','Delivered'), ('cancelled','Cancelled')]
    PAYMENT_METHOD = [('cod','Cash on Delivery'), ('khalti','Khalti'), ('esewa','eSewa'), ('card','Credit / Debit Card'), ('fonepay','Fonepay')]
    PAYMENT_STATUS = [('unpaid','Unpaid'), ('paid','Paid'), ('failed','Failed')]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD, default='cod')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='unpaid')
    payment_token = models.CharField(max_length=200, blank=True)
    transaction_uuid = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} – {self.full_name}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    size = models.CharField(max_length=10, blank=True)

    @property
    def subtotal(self):
        return self.price * self.quantity
