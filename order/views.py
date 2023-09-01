import datetime
from django.shortcuts import render, redirect
from django.views import View
from .forms import CartQuantityForm, OrderForm, CouponForm
from django.shortcuts import get_object_or_404
from product.models import WatchVariantModel
from .models import CouponModel, OrderModel, OrderItemModel
from django.contrib import messages
from .cart import CART_SESSION_ID, Cart
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
import json
import requests
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse
from utils import send_otp_code
from accounts.models import CostumeUserModel



class OrderView(View):
    def get(self, request):
        # cart.clear_cart_session()
        context = {
            'is_cart_editable': True
        }
        return render(request, 'accounts/profile/profile.html', context)


class CartAddView(View):
    form_class = CartQuantityForm
    def post(self, request, variant_id):
        cart = Cart(request)
        variant = get_object_or_404(WatchVariantModel, id=variant_id)
        form = self.form_class(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart.add(request, variant, quantity)
        return redirect('order:show_order')


class CartAddOneView(View):
    def get(self, request, variant_id):
        cart = Cart(request)
        variant = get_object_or_404(WatchVariantModel, id=variant_id)
        cart.add(request, variant, 1)
        if variant.quantity == request.session[CART_SESSION_ID][str(variant.id)]['quantity']:
            should_hide = True
        else:
            should_hide = False

        price = {}
        for i in request.session[CART_SESSION_ID].keys():
            price[i] = float(request.session[CART_SESSION_ID][i]['price'])*int(request.session[CART_SESSION_ID][i]['quantity'])
        data = {
            'should_hide': should_hide,
            'quantity': request.session[CART_SESSION_ID][str(variant.id)]['quantity'],
            'variant_id': str(variant.id),
            'price': price,
            'total_price': cart.get_total_price(),
            'cart_len': len(cart)
        }
        return JsonResponse(data)


class CartRemoveOneView(View):
    def get(self, request, variant_id):
        cart = Cart(request)
        variant = get_object_or_404(WatchVariantModel, id=variant_id)
        cart.remove_one(variant)
        try:
            a=request.session[CART_SESSION_ID]
            should_hide = False
            quantity = request.session[CART_SESSION_ID][str(variant.id)]['quantity']
        except KeyError:
            should_hide = True
            quantity = 0
        price = {}
        for i in request.session[CART_SESSION_ID].keys():
            price[i] = float(request.session[CART_SESSION_ID][i]['price'])*int(request.session[CART_SESSION_ID][i]['quantity'])
        data = {
            'should_hide': should_hide,
            'quantity': quantity,
            'variant_id': str(variant.id),
            'total_price': cart.get_total_price(),
            'price': price,
            'cart_len': len(cart)
        }
        return JsonResponse(data)


class CartRemoveView(View):
    def get(self, request, variant_id):
        cart = Cart(request)
        variant = get_object_or_404(WatchVariantModel, id=variant_id)
        cart.remove(variant)
        data = {
            'variant_id': variant.id,
            'total_price': cart.get_total_price(),
            'cart_len': len(cart)
        }
        return JsonResponse(data)


class OrderSubmitView(View):
    form_class = OrderForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت ثبت نام کنید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        order_form = self.form_class()

        context = {
            'order_form': order_form,
            'is_cart_editable': False
        }
        return render(request, 'order/order_submit.html', context)


class CouponView(View):
    form_class = CouponForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت ثبت نام کنید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            coupon_code = form.cleaned_data['coupon']
            try:
                coupon = CouponModel.objects.get(coupon_code__exact=coupon_code)
                now = datetime.datetime.now(coupon.start_time.tzinfo)
                if not coupon.is_active:
                    messages.warning(request, 'کد تخفیف وارد شده غیرفعال است', 'msg-bg-warning')
                    return redirect('order:submit_order')
                elif coupon.start_time > now:
                    messages.warning(request, 'کد تخفیف وارد شده هنوز فعال نشده است', 'msg-bg-warning')
                    return redirect('order:submit_order')
                elif coupon.end_time < now:
                    messages.warning(request, 'کد تخفیف وارد شده منقضی شده است', 'msg-bg-warning')
                    return redirect('order:submit_order')
            except CouponModel.DoesNotExist:
                messages.warning(request, 'کد تخفیف وارد شده موجود نمیباشد', 'msg-bg-warning')
                return redirect('order:submit_order')

            if coupon.is_one_used:
                coupon = CouponModel.objects.filter(coupon_code__exact=coupon_code, is_one_used=True, user=request.user).first()
                if coupon:
                    Cart(request).coupon(request, coupon_code, coupon.discount)
                    messages.success(request, 'کد تخفیف شما با موفقیت اعمال شد', 'msg-bg-success')
                else:
                    messages.warning(request, 'کد تخفیف وارد شده قابل استفاده نمیباشد', 'msg-bg-warning')
            else:
                Cart(request).coupon(request, coupon_code, coupon.discount)
                messages.success(request, 'کد تخفیف شما با موفقیت اعمال شد', 'msg-bg-success')
            return redirect('order:submit_order')
        else:
            try:
                del request.session['coupon']
            except KeyError:
                pass
            return redirect('order:submit_order')




class CreateOrderView(PermissionRequiredMixin, View):
    permission_required = ('order.add_ordermodel',)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        cart = Cart(request)
        form = OrderForm(request.POST)

        now = datetime.datetime.now()
        if form.is_valid():
            cd = form.cleaned_data
            try:
                coupon = CouponModel.objects.filter(coupon_code__exact=request.session['coupon']['coupon_code']).first()
                if coupon:
                    order = OrderModel.objects.create(
                        user=request.user,
                        gp_f_name=cd['gp_f_name'],
                        gp_l_name=cd['gp_l_name'],
                        gp_phone=cd['gp_phone'],
                        gp_postal_code=cd['gp_postal_code'],
                        gp_address=cd['gp_address'],
                        coupon=coupon
                    )
                    coupon.user.remove(request.user)
            except KeyError:
                order = OrderModel.objects.create(
                    user=request.user,
                    gp_f_name=cd['gp_f_name'],
                    gp_l_name=cd['gp_l_name'],
                    gp_phone=cd['gp_phone'],
                    gp_postal_code=cd['gp_postal_code'],
                    gp_address=cd['gp_address']
                )
            carts = request.session[CART_SESSION_ID]
            for item in carts:
                OrderItemModel.objects.create(
                    order=order,
                    variant_id=item,
                    quantity=carts[item]['quantity'],
                    price=carts[item]['price']
                )
            cart.clear_cart_session()
            cart.clear_coupon_session()
        else:
            messages.warning(request, 'لطفا همه اطلاعات فوق را تکمیل کنید', 'msg-bg-warning')
            return redirect('order:submit_order')
        return redirect('order:zp_simulator')
        # return redirect('order:zp_send_request')


if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'
ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"
CallbackURL = 'http://127.0.0.1:8000/order/zpVerify'


class SendRequest(LoginRequiredMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id)
        request.session['order'] = {
            'order_id': order.id
        }
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.get_total_cost * 10,
            "Description": 'watch store payment',
            "Phone": request.user.phone,
            "CallbackURL": CallbackURL,
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                            'authority': response['Authority']}
                else:
                    return {'status': False, 'code': str(response['Status'])}
            return response

        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection error'}


class VerifyPay(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, authority):
        order_id = int(request.session['order']['order_id'])
        order = get_object_or_404(OrderModel, id=order_id)
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": order.get_total_cost,
            "Authority": authority,
        }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                order.paid = True
                order.save()
                selected_variants = order.rel_order_items.all()
                user = get_object_or_404(CostumeUserModel, id=request.user.id)
                for v in selected_variants:
                    variant = WatchVariantModel.objects.get(id=v.id)
                    variant.quantity -= v.quantity
                    if variant.quantity == 0:
                        variant.is_required = False
                    variant.total_sale += v.quantity
                    variant.save()
                    user.total_buy += v.quantity
                    user.save()
                send_otp_code(request.user.phone, f'عزیز سفارش شما با موقیت ثبت شد{request.user.f_name} {request.user.l_name}')
                # send_otp_code(amir phone, f'user:{request.user.f_name} {request.user.l_name}\norder:{order.id}\nphone:{request.user.phone}')
                # send_otp_code(hamid phone, f'user:{request.user.f_name} {request.user.l_name}\norder:{order.id}\nphone:{request.user.phone}')
                cntx_success = {
                    'status': True,
                    'RefID': response['RefID']
                }
                return render(request, 'order/zarinpal_result.html', cntx_success)
            else:
                cntx_fail = {
                    'status': False,
                    'code': str(response['Status'])
                }
                return render(request, 'order/zarinpal_result.html', cntx_fail)
        return response


class ZarinPalSimulator(View):
    def get(self, request):
        cntx = {
            'status': True,
            'RefID': 123456789,
        }
        return render(request, 'order/zarinpal_result.html', cntx)


class LastOrdersView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'user_orders': OrderModel.objects.filter(user_id=request.user.id, paid=True),
            'is_user_orders_page': True
        }
        return render(request, 'accounts/profile/profile.html', context)
