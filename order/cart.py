from product.models import WatchVariantModel
from django.shortcuts import get_object_or_404
from django.contrib import messages

CART_SESSION_ID = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(CART_SESSION_ID)
        if not self.cart:
            self.session[CART_SESSION_ID] = {}
        self.cart = self.session[CART_SESSION_ID]

    def __iter__(self):
        variant_ids = self.cart.keys()
        variants = WatchVariantModel.objects.filter(id__in=variant_ids)
        cart = self.cart.copy()
        for v in variants:
            cart[str(v.id)]['variant'] = v
        for item in cart.values():
            item['total_price'] = float(item['price']) * int(item['quantity'])
            yield item

    def __len__(self):
        return sum(int(item['quantity']) for item in self.cart.values())

    def add(self, request, variant, quantity):
        variant_id = str(variant.id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {
                'quantity': 0,
                'price': str(variant.final_price),
            }
        self.cart[variant_id]['quantity'] += quantity
        if self.cart[variant_id]['quantity'] > get_object_or_404(WatchVariantModel, id=variant_id).quantity:
            self.cart[variant_id]['quantity'] = get_object_or_404(WatchVariantModel, id=variant_id).quantity
        self.save()

    def remove(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def remove_one(self, variant):
        variant_id = str(variant.id)
        if variant_id in self.cart:
            self.cart[variant_id]['quantity'] -= 1
            self.save()
        if self.cart[variant_id]['quantity'] == 0:
            del self.cart[variant_id]
            self.save()

    def clear_cart_session(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def get_total_price(self):
        return sum([float(item['price']) * int(item['quantity']) for item in self.cart.values()])

    def coupon(self, request, code, discount):
        request.session['coupon'] = {
            'coupon_code': code,
            'coupon_discount': int(discount),
            'get_total_price_coupon': self.get_total_price() * (100 - discount) / 100
        }
        self.save()

    def clear_coupon_session(self):
        self.session['coupon'] = {}
        self.save()

    def save(self):
        self.session.modified = True
