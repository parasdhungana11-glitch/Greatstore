from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem

admin.site.site_header  = '🛍️ GreatStore Admin'
admin.site.site_title   = 'GreatStore'
admin.site.index_title  = 'Welcome to GreatStore Dashboard'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['name', 'category', 'price', 'discount_badge', 'stock', 'is_featured', 'rating', 'created_at']
    list_filter   = ['category', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Info',   {'fields': ('name', 'slug', 'category', 'description')}),
        ('Pricing',      {'fields': ('price', 'original_price')}),
        ('Media & Shop', {'fields': ('image_url', 'daraz_url', 'stock')}),
        ('Flags',        {'fields': ('is_featured', 'rating', 'created_at')}),
    )

    @admin.display(description='Discount')
    def discount_badge(self, obj):
        if obj.discount_percent:
            return f'-{obj.discount_percent}%'
        return '—'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_at']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'full_name', 'email', 'total', 'payment_method', 'payment_status', 'status', 'created_at']
    list_filter   = ['status', 'payment_method', 'payment_status']
    list_editable = ['status']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'transaction_uuid', 'payment_token']
    inlines = [OrderItemInline]
