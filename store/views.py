from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .payment import (
    khalti_initiate, khalti_verify,
    esewa_form_data, esewa_verify, generate_transaction_uuid,
)
import json
import base64


def _get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def home(request):
    categories = Category.objects.all()
    featured = Product.objects.filter(is_featured=True).select_related('category')[:8]
    new_arrivals = Product.objects.select_related('category').order_by('-created_at')[:8]
    return render(request, 'index.html', {
        'categories': categories,
        'featured_products': featured,
        'new_arrivals': new_arrivals,
    })


def store(request):
    categories = Category.objects.all()
    products = Product.objects.select_related('category').all()

    category_slug = request.GET.get('category')
    price_min = request.GET.get('min_price')
    price_max = request.GET.get('max_price')
    sort = request.GET.get('sort', 'newest')
    active_category = None

    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    else:
        products = products.order_by('-created_at')

    return render(request, 'store.html', {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'total_count': products.count(),
        'sort': sort,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'product-detail.html', {
        'product': product,
        'related_products': related,
    })


def cart_view(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': items,
        'cart_total': cart.get_total(),
    })


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_or_create_cart(request)
    size = request.POST.get('size', 'M')
    quantity = int(request.POST.get('quantity', 1))

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, size=size)
    if not created:
        item.quantity += quantity
    else:
        item.quantity = quantity
    item.save()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_count': cart.item_count()})
    messages.success(request, f'"{product.name}" added to cart.')
    return redirect('cart')


@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__session_key=request.session.session_key)
    item.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = _get_or_create_cart(request)
        return JsonResponse({'success': True, 'cart_count': cart.item_count(), 'cart_total': float(cart.get_total())})
    return redirect('cart')


def place_order(request):
    cart = _get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    if not items.exists():
        return redirect('cart')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cod')
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key,
            full_name=request.POST['full_name'],
            email=request.POST['email'],
            address=request.POST['address'],
            phone=request.POST['phone'],
            total=cart.get_total(),
            payment_method=payment_method,
            payment_status='unpaid',
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
                size=item.size,
            )
        cart.items.all().delete()

        if payment_method == 'khalti':
            return redirect('khalti_pay', order_id=order.id)
        elif payment_method == 'esewa':
            return redirect('esewa_pay', order_id=order.id)
        elif payment_method == 'card':
            return redirect('card_pay', order_id=order.id)
        elif payment_method == 'fonepay':
            return redirect('fonepay_pay', order_id=order.id)
        else:
            order.payment_status = 'unpaid'
            order.save()
            return redirect('order_complete', order_id=order.id)

    return render(request, 'place-order.html', {
        'cart_items': items,
        'cart_total': cart.get_total(),
    })


def order_complete(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_complete.html', {'order': order})


def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query)
    ).select_related('category') if query else Product.objects.none()
    return render(request, 'search-result.html', {'products': products, 'query': query})


def signin_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'signin.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST.get('password2', '')
        if password != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, f'Welcome to GreatStore, {username}!')
            return redirect('home')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('signin')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard.html', {'orders': orders})


# ── Khalti Payment Views ─────────────────────────────────────────────────────

def khalti_pay(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    try:
        return_url = request.build_absolute_uri(reverse('khalti_callback'))
        website_url = request.build_absolute_uri('/')
        pidx, payment_url = khalti_initiate(order, return_url, website_url)
        order.payment_token = pidx
        order.save()
        return redirect(payment_url)
    except Exception as e:
        messages.error(request, f'Khalti error: {e}')
        return redirect('order_complete', order_id=order.id)


def khalti_callback(request):
    pidx = request.GET.get('pidx')
    status = request.GET.get('status')
    purchase_order_id = request.GET.get('purchase_order_id')

    order = get_object_or_404(Order, id=purchase_order_id)

    if status == 'Completed' and pidx:
        try:
            data = khalti_verify(pidx)
            if data.get('status') == 'Completed':
                order.payment_status = 'paid'
                order.payment_token = pidx
                order.save()
                messages.success(request, 'Payment successful via Khalti!')
                return redirect('order_complete', order_id=order.id)
        except Exception:
            pass

    order.payment_status = 'failed'
    order.save()
    messages.error(request, 'Khalti payment was not completed.')
    return redirect('payment_failed', order_id=order.id)


# ── eSewa Payment Views ──────────────────────────────────────────────────────

def esewa_pay(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    txn_uuid = generate_transaction_uuid()
    order.transaction_uuid = txn_uuid
    order.save()

    success_url = request.build_absolute_uri(reverse('esewa_callback_success'))
    failure_url = request.build_absolute_uri(reverse('esewa_callback_failure', args=[order.id]))
    form_data = esewa_form_data(order, txn_uuid, success_url, failure_url)

    return render(request, 'esewa_redirect.html', {
        'esewa_url': settings.ESEWA_PAYMENT_URL,
        'form_data': form_data,
        'order': order,
    })


def esewa_callback_success(request):
    # eSewa sends base64-encoded JSON in ?data= param
    encoded = request.GET.get('data', '')
    try:
        decoded = base64.b64decode(encoded).decode('utf-8')
        data = json.loads(decoded)
        txn_uuid = data.get('transaction_uuid')
        status = data.get('status')
        total_amount = data.get('total_amount')

        order = Order.objects.filter(transaction_uuid=txn_uuid).first()
        if order and status == 'COMPLETE':
            # Verify with eSewa API
            verify = esewa_verify(settings.ESEWA_MERCHANT_CODE, total_amount, txn_uuid)
            if verify.get('status') == 'COMPLETE':
                order.payment_status = 'paid'
                order.payment_token = data.get('ref_id', '')
                order.save()
                messages.success(request, 'Payment successful via eSewa!')
                return redirect('order_complete', order_id=order.id)
    except Exception:
        pass

    messages.error(request, 'eSewa payment verification failed.')
    return redirect('home')


def esewa_callback_failure(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.payment_status = 'failed'
    order.save()
    messages.error(request, 'eSewa payment was cancelled or failed.')
    return redirect('payment_failed', order_id=order.id)


def payment_failed(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment_failed.html', {'order': order})


# ── Card Payment Views ───────────────────────────────────────────────────────

def card_pay(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # In production: tokenize card with iPay / Stripe and charge here
        # For demo: mark as paid directly
        card_number = request.POST.get('card_number', '').replace(' ', '')
        expiry = request.POST.get('expiry', '')
        cvv = request.POST.get('cvv', '')
        name = request.POST.get('card_name', '')

        if len(card_number) < 13 or not expiry or len(cvv) < 3 or not name:
            messages.error(request, 'Please fill in all card details correctly.')
            return render(request, 'card_pay.html', {'order': order})

        order.payment_status = 'paid'
        order.payment_token = f'CARD-{card_number[-4:]}'
        order.save()
        messages.success(request, 'Card payment successful!')
        return redirect('order_complete', order_id=order.id)

    return render(request, 'card_pay.html', {'order': order})


# ── Fonepay / Phone Pay Views ────────────────────────────────────────────────

def fonepay_pay(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    txn_uuid = generate_transaction_uuid()
    order.transaction_uuid = txn_uuid
    order.save()

    success_url = request.build_absolute_uri(reverse('fonepay_callback', args=[order.id]))
    # Fonepay production params — replace PRN and username with your merchant credentials
    fonepay_params = {
        'PID': 'FONEPAY_MERCHANT_ID',   # Replace with your Fonepay merchant ID
        'MD': 'P',
        'AMT': str(order.total),
        'CRN': 'NPR',
        'DT': order.created_at.strftime('%m/%d/%Y'),
        'R1': f'GreatStore Order #{order.id}',
        'R2': 'Payment',
        'RU': success_url,
        'PRN': txn_uuid,
    }
    return render(request, 'fonepay_pay.html', {
        'order': order,
        'fonepay_url': 'https://dev.fonepay.com/api/merchant/merchantDetailsForThirdParty',
        'fonepay_params': fonepay_params,
    })


def fonepay_callback(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    ps = request.GET.get('PS', '')       # Payment status: success/failure
    prn = request.GET.get('PRN', '')

    if ps.lower() == 'success' and prn == order.transaction_uuid:
        order.payment_status = 'paid'
        order.payment_token = request.GET.get('BID', prn)
        order.save()
        messages.success(request, 'Fonepay payment successful!')
        return redirect('order_complete', order_id=order.id)

    order.payment_status = 'failed'
    order.save()
    messages.error(request, 'Fonepay payment failed or was cancelled.')
    return redirect('payment_failed', order_id=order.id)
