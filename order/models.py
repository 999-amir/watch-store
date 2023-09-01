from django.db import models
from accounts.models import CostumeUserModel
from product.models import WatchVariantModel
from accounts.models import CostumeUserModel


class CouponModel(models.Model):
    coupon_code = models.CharField(max_length=20)
    discount = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    is_one_used = models.BooleanField(default=False)
    user = models.ManyToManyField(CostumeUserModel, blank=True)

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'


class OrderModel(models.Model):
    user = models.ForeignKey(CostumeUserModel, on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='rel_orders')
    coupon = models.ForeignKey(CouponModel, on_delete=models.SET_NULL, null=True, blank=True)
    # person who give watch ( not who buy it )
    gp_f_name = models.CharField(max_length=100)
    gp_l_name = models.CharField(max_length=100)
    gp_phone = models.CharField(max_length=11)
    gp_address = models.TextField()
    gp_postal_code = models.CharField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def get_total_cost(self):
        total = sum([item.get_cost for item in self.rel_order_items.all()])
        if self.coupon:
            total *= (100 - float(self.coupon.discount)) / 100
        return total

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='rel_order_items')
    variant = models.ForeignKey(WatchVariantModel, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.quantity} {self.price}'

    @property
    def get_cost(self):
        return self.quantity * self.price

    class Meta:
        verbose_name = 'جز سفارش'
        verbose_name_plural = 'اجزا سفارشات'
