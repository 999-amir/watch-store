from django.contrib import admin
from .models import OrderItemModel, OrderModel, CouponModel
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date import datetime2jalali


def fa_start_time(model):
    return datetime2jalali(model.start_time).strftime('%Y/%m/%d _ %H:%M:%S')

def fa_end_time(model):
    return datetime2jalali(model.end_time).strftime('%Y/%m/%d _ %H:%M:%S')

@admin.register(CouponModel)
class CouponAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ('coupon_code', 'discount', 'is_active', 'is_one_used', fa_start_time, fa_end_time)
    fieldsets = (
        (
            'coupon',
            {'fields': ('coupon_code', 'discount', 'is_active')}
        ),
        (
            'activation date',
            {'fields': ('start_time', 'end_time')}
        ),
        (
            'allowed users',
            {'fields': ('is_one_used', 'user')}
        ),
    )
    list_editable = ('is_active', 'is_one_used')
    list_filter = ('discount', 'is_active', 'is_one_used', 'start_time', 'end_time', 'updated')
    filter_horizontal = ('user',)


@admin.register(OrderItemModel)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'variant', 'quantity', 'price', 'get_cost')


class OrderItemInline(admin.TabularInline):
    model = OrderItemModel
    extra = 1
    raw_id_fields = ('order',)


def fa_updated(model):
    return datetime2jalali(model.updated).strftime('%Y/%m/%d _ %H:%M:%S')


@admin.register(OrderModel)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('gp_f_name', 'gp_l_name', 'gp_phone', 'get_total_cost', 'paid', fa_updated)
    fieldsets = (
        (
            'who cost it',
            {'fields': ('user', 'coupon')}
        ),
        (
            'who give it',
            {'fields': ('paid', 'gp_f_name', 'gp_l_name', 'gp_phone', 'gp_address', 'gp_postal_code')}
        )
    )
    list_filter = ('gp_phone', 'paid', 'updated')
    inlines = (OrderItemInline,)

