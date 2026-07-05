from .models import Cart, Category


def cart_count(request):
    count = 0
    try:
        if not request.session.session_key:
            request.session.create()
        cart = Cart.objects.filter(session_key=request.session.session_key).first()
        if cart:
            count = cart.item_count()
    except Exception:
        pass
    categories = Category.objects.all()
    return {'cart_count': count, 'categories': categories}
