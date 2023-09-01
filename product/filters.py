import django_filters
from django import forms
from . import models as m


class WatchFilterRequired(django_filters.FilterSet):
    SORTED_PRICE = (
        ('exp', 'most expensive'),
        ('chp', 'most cheapest'),
    )
    SORTED_DISCOUNT = (
        ('mostDiscount', 'most discount'),
    )
    SORTED_SALE = (
        ('mostSale', 'most sale'),
    )
    SORTED_SEEN = (
        ('mostSeen', 'most seen'),
    )
    SORTED_FAVORITE = (
        ('mostFav', 'most favorites'),
    )
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='lte')
    brand = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchBrandModel.objects.all())
    face_shape = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchFaceShapeModel.objects.all())
    face_material = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchFaceMaterialModel.objects.all())
    band_material = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchBandMaterialModel.objects.all())
    system = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchSystemModel.objects.all())
    band_lock = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchBandLockModel.objects.all())
    sorted_price = django_filters.ChoiceFilter(choices=SORTED_PRICE, method='sort_price')
    sorted_discount = django_filters.ChoiceFilter(choices=SORTED_DISCOUNT, method='sort_discount')
    sorted_sale = django_filters.ChoiceFilter(choices=SORTED_SALE, method='sort_sale')
    sorted_seen = django_filters.ChoiceFilter(choices=SORTED_SEEN, method='sort_seen')
    sorted_favorite = django_filters.ChoiceFilter(choices=SORTED_FAVORITE, method='sort_favorite')

    def sort_price(self, queryset, name, value):
        data = 'min_price' if value=='chp' else '-min_price'
        return queryset.order_by(data)

    def sort_discount(self, queryset, name, value):
        return queryset.order_by('-variant_discount_min_price')

    def sort_sale(self, queryset, name, value):
        return queryset.order_by('-variant_sale')

    def sort_seen(self, queryset, name, value):
        return queryset.order_by('-total_seen')

    def sort_favorite(self, queryset, name, value):
        return queryset.order_by('-total_favorite')


class WatchFilterUnrequired(django_filters.FilterSet):
    brand = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchBrandModel.objects.all())
    face_shape = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchFaceShapeModel.objects.all())
    face_material = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchFaceMaterialModel.objects.all())
    band_material = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchBandMaterialModel.objects.all())
    system = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchSystemModel.objects.all())
    band_lock = django_filters.ModelMultipleChoiceFilter(queryset=m.WatchBandLockModel.objects.all())