from .cart import Cart, CART_SESSION_ID


def cp_cart(request):
    cart = Cart(request)
    context = {
        'carts': cart,
        'get_total_price': cart.get_total_price(),
    }
    try:
        context['get_total_price_coupon'] = request.session['coupon']['get_total_price_coupon']
        context['coupon_discount'] = request.session['coupon']['coupon_discount']
    except KeyError:
        pass
    return context
