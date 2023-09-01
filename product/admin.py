from django.contrib import admin
from . import models as m
from jalali_date import datetime2jalali

def fa_updated(model):
    return datetime2jalali(model.updated).strftime('%Y/%m/%d _ %H:%M:%S')

@admin.register(m.CarouselModel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('text', 'image', 'brightness', fa_updated)
    list_editable = ('brightness',)
    list_filter = ('updated',)
    fieldsets = (
        (
            'carousel',
            {'fields': ('text', 'image', 'brightness')},
        ),
    )


admin.site.register(m.WatchBrandModel)
admin.site.register(m.WatchFaceMaterialModel)
admin.site.register(m.WatchFaceShapeModel)
admin.site.register(m.WatchSystemModel)
admin.site.register(m.WatchBandMaterialModel)
admin.site.register(m.WatchBandLockModel)


@admin.register(m.WatchColorModel)
class WatchColorAdmin(admin.ModelAdmin):
    list_display = ('color_name', 'hex_color')


class WatchVariantInline(admin.TabularInline):
    model = m.WatchVariantModel
    can_delete = True
    extra = 1


class WatchImageInline(admin.TabularInline):
    model = m.WatchImageModel
    can_delete = True
    extra = 1


@admin.register(m.WatchModel)
class WatchAdmin(admin.ModelAdmin):
    list_display = (
    'brand', 'name', 'is_required', 'min_price', 'variants_total_sale',
    'total_seen', 'total_favorite', fa_updated)
    list_editable = ('is_required',)
    fieldsets = (
        (
            'model',
            {'fields': ('is_required', 'brand', 'name', 'slug', 'info')}
        ),
        (
            'shape & material',
            {'fields': (
            'face_diameter', 'face_thickness', 'face_shape', 'face_material', 'system', 'band_material', 'band_lock')}
        ),
        (
            'user like & bookmark',
            {'fields': ('likes', 'bookmark')}
        )
    )
    prepopulated_fields = {
        'slug': ('name',)
    }
    raw_id_fields = ('brand',)
    filter_horizontal = ('likes', 'bookmark')
    inlines = (WatchVariantInline, WatchImageInline)
    list_filter = ('is_required', 'updated')


class PriceChangeVariantInline(admin.TabularInline):
    model = m.PriceChangeVariantModel
    can_delete = True
    extra = 1


def fa_created(model):
    return datetime2jalali(model.created).strftime('%Y/%m/%d _ %H:%M:%S')

@admin.register(m.WatchVariantModel)
class WatchVariantAdmin(admin.ModelAdmin):
    list_display = (
    'watch', 'is_required', 'face_color', 'first_price', 'profit', 'discount', 'quantity', 'final_price_fob',
    'total_sale', fa_created)
    list_editable = ('profit', 'discount', 'quantity', 'is_required')
    fieldsets = (
        (
            'color',
            {'fields': ('watch', 'is_required', 'face_color',)}
        ),
        (
            'price & quantity',
            {'fields': ('quantity', 'first_price', 'profit', 'discount')}
        ),
    )
    raw_id_fields = ('watch', 'face_color')
    inlines = (PriceChangeVariantInline,)
    list_filter = ('is_required', 'face_color', 'profit', 'discount', 'quantity', 'watch', 'updated')


def fa_date(model):
    return datetime2jalali(model.date).strftime('%Y/%m/%d _ %H:%M:%S')


# @admin.register(m.PriceChangeVariantModel)
# class PriceChangeVariantAdmin(admin.ModelAdmin):
#     list_display = ('variant', 'price', fa_date)
#     raw_id_fields = ('variant',)


@admin.register(m.CommentModel)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'can_show', 'is_reply', 'reply')
    list_editable = ('can_show',)
    list_filter = ('is_reply', 'can_show', 'product', 'user', 'updated')
