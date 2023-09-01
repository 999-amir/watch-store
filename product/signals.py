from django.db.models.signals import post_save
from .models import WatchVariantModel, PriceChangeVariantModel
from django.dispatch import receiver


# this page writed sooooo f***ing hard

@receiver(post_save, sender=WatchVariantModel)
def price_change_variant_create(sender, **kwargs):
    variant = kwargs['instance']
    if kwargs['created']:
        if variant.watch.is_required is False:
            variant.watch.is_required = True
            variant.watch.save()
        PriceChangeVariantModel.objects.create(variant=variant, price=variant.final_price)
    else:
        last_price = PriceChangeVariantModel.objects.filter(variant=variant).order_by('-date').first()
        if last_price is not None:
            if last_price.price != variant.final_price:
                PriceChangeVariantModel.objects.create(variant=variant, price=variant.final_price)
        else:
            PriceChangeVariantModel.objects.create(variant=variant, price=variant.final_price)
        if variant.is_required is True:
            variant.watch.is_required = True
            variant.watch.save()


@receiver(post_save, sender=WatchVariantModel)
def final_price_fob(sender, **kwargs):
    variant = kwargs['instance']
    var_last_price = WatchVariantModel.objects.get(id=variant.id)
    if var_last_price.final_price_fob != variant.final_price:
        var_last_price.final_price_fob = variant.final_price
        var_last_price.save()


@receiver(post_save, sender=WatchVariantModel)
def min_price_watch(sender, **kwargs):
    variant = kwargs['instance']
    last_min_price_var = WatchVariantModel.objects.filter(id=variant.watch.variant_id_min_price,
                                                          is_required=True).first()
    if last_min_price_var and variant.is_required:  # when variant will be change ( it has another variant )
        last_min_price = last_min_price_var.final_price
        if variant.final_price < last_min_price:
            variant.watch.variant_id_min_price = variant.id
            variant.watch.min_price = variant.final_price
            variant.watch.save()
    elif variant.is_required:  # when new variant will be born
        variant.watch.variant_id_min_price = variant.id
        variant.watch.min_price = variant.final_price
        variant.watch.save()
    else:
        cheapest_var = WatchVariantModel.objects.filter(watch=variant.watch, is_required=True).order_by(
            'final_price_fob').first()
        if cheapest_var:
            variant.watch.variant_id_min_price = cheapest_var.id
            variant.watch.min_price = cheapest_var.final_price
            variant.watch.save()
        else:  # it means all variants quantity is equal with 0 so watch should be unrequired
            variant.watch.variant_id_min_price = variant.id  # because there is only one variant exist and it's quantity will be 0 soon after signal
            variant.watch.min_price = variant.final_price
            variant.watch.is_required = False
            variant.watch.save()


@receiver(post_save, sender=WatchVariantModel)
def quantity_min_price(sender, **kwargs):
    variant = kwargs['instance']
    variant_min_price = WatchVariantModel.objects.get(id=variant.watch.variant_id_min_price)
    if variant.watch.variant_discount_min_price != variant_min_price.discount or variant.watch.variant_sale != variant.watch.variants_total_sale:
        variant.watch.variant_discount_min_price = variant_min_price.discount
        if variant_min_price.is_required:
            variant.watch.variant_sale = variant.watch.variants_total_sale
        variant.watch.save()
