from django import forms
from .models import OrderModel


class CartQuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1)


class OrderForm(forms.ModelForm):
    class Meta:
        model = OrderModel
        fields = ('gp_f_name', 'gp_l_name', 'gp_phone', 'gp_address', 'gp_postal_code')


class CouponForm(forms.Form):
    coupon = forms.CharField(max_length=20)
