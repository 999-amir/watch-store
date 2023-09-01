from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from accounts.models import CostumeUserModel
from jalali_date import datetime2jalali


class CarouselModel(models.Model):
    image = models.ImageField(upload_to='media/carousel_image')
    text = models.CharField(max_length=100, null=True, blank=True)
    brightness = models.PositiveIntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = 'تصویر متحرک'
        verbose_name_plural = 'تصاویر متحرک صفحه اصلی'


class WatchBrandModel(models.Model):
    Brand = models.CharField(max_length=100)
    image = models.ImageField(upload_to='media/brand/%y/%m/', null=True, blank=True)

    def __str__(self):
        return self.Brand

    class Meta:
        verbose_name = 'برند ساعت'
        verbose_name_plural = 'برندهای ساعت'


class WatchBandMaterialModel(models.Model):
    band_material = models.CharField(max_length=100)

    def __str__(self):
        return self.band_material

    class Meta:
        verbose_name = 'جنس ساعت'
        verbose_name_plural = 'جنس های ساعت'


class WatchBandLockModel(models.Model):
    lock = models.CharField(max_length=100)

    def __str__(self):
        return self.lock

    class Meta:
        verbose_name = 'نوع قفل'
        verbose_name_plural = 'انواع قفل ساعت'


class WatchFaceShapeModel(models.Model):
    shape = models.CharField(max_length=100)

    def __str__(self):
        return self.shape

    class Meta:
        verbose_name = 'طرح صفحه'
        verbose_name_plural = 'طرح های صفحه ساعت'


class WatchFaceMaterialModel(models.Model):
    face_material = models.CharField(max_length=100)

    def __str__(self):
        return self.face_material

    class Meta:
        verbose_name = 'جنس بدنه'
        verbose_name_plural = 'جنس های بدنه ساعت'


class WatchSystemModel(models.Model):
    system = models.CharField(max_length=100)

    def __str__(self):
        return self.system

    class Meta:
        verbose_name = 'موتور ساعت'
        verbose_name_plural = 'موتور های ساعت'


class WatchColorModel(models.Model):
    hex_color = models.CharField(max_length=100)
    color_name = models.CharField(max_length=100)

    def __str__(self):
        return self.color_name

    class Meta:
        verbose_name = 'رنگ'
        verbose_name_plural = 'انواع رنگ ساعت'


class WatchModel(models.Model):
    brand = models.ForeignKey(WatchBrandModel, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='rel_watch_brands')
    name = models.CharField(max_length=100)
    info = RichTextField()
    slug = models.SlugField(null=True, blank=True)
    face_diameter = models.PositiveIntegerField()
    face_thickness = models.PositiveIntegerField()
    is_required = models.BooleanField(default=True)
    band_material = models.ForeignKey(WatchBandMaterialModel, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='rel_band_mat')
    band_lock = models.ForeignKey(WatchBandLockModel, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='rel_band_lock')
    face_shape = models.ForeignKey(WatchFaceShapeModel, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='rel_face_shape')
    face_material = models.ForeignKey(WatchFaceMaterialModel, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='rel_face_mat')
    system = models.ForeignKey(WatchSystemModel, on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='rel_system')
    total_seen = models.PositiveIntegerField(default=0)
    total_favorite = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    variant_id_min_price = models.PositiveIntegerField(null=True, blank=True)
    min_price = models.PositiveIntegerField(null=True, blank=True)
    variant_discount_min_price = models.PositiveIntegerField(null=True, blank=True)
    variant_sale = models.PositiveIntegerField(null=True, blank=True)
    likes = models.ManyToManyField(CostumeUserModel, blank=True)
    bookmark = models.ManyToManyField(CostumeUserModel, blank=True, related_name='rel_bookmarks')

    def __str__(self):
        return f'{self.brand} - {self.name}'

    @property
    def lowest_quantity(self):
        lq = self.rel_watch_variants.filter(quantity__lt=4).order_by('quantity')
        if len(lq) != 0:
            return lq[0].quantity
        else:
            return False

    def get_absolute_url(self):
        return reverse('product:details', args=(self.pk, self.slug))

    @property
    def variants_total_sale(self):
        return sum([item.total_sale for item in self.rel_watch_variants.all()])

    def like_checker(self, user):
        if self.likes.filter(id=user.id):
            return True
        else:
            return False

    def bookmark_checker(self, user):
        if self.bookmark.filter(id=user.id):
            return True
        else:
            return False

    class Meta:
        verbose_name = 'ساعت'
        verbose_name_plural = 'ساعت ها'


class WatchVariantModel(models.Model):
    watch = models.ForeignKey(WatchModel, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='rel_watch_variants')
    face_color = models.ForeignKey(WatchColorModel, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='rel_face_colors')
    discount = models.PositiveIntegerField(null=True, blank=True)
    first_price = models.PositiveIntegerField(null=True, blank=True)
    profit = models.PositiveIntegerField(null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_sale = models.PositiveIntegerField(default=0)
    is_required = models.BooleanField(default=True)
    final_price_fob = models.PositiveIntegerField(default=0)  # fob -> for function order_by

    @property
    def final_price(self):
        global f_price
        if self.first_price is not None:
            f_price = float(self.first_price)
        if self.profit is not None:
            f_price *= (100 + float(self.profit)) / 100
        if self.discount is not None:
            f_price *= (100 - float(self.discount)) / 100

        return int(f_price)

    class Meta:
        verbose_name = 'مدل ساعت'
        verbose_name_plural = 'مدل های ساعت'


class WatchImageModel(models.Model):
    watch = models.ForeignKey(WatchModel, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='rel_watch_images')
    image = models.ImageField(upload_to='media/products/%y/%m/%d')
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.watch.brand} {self.watch.name}'

    class Meta:
        verbose_name = 'عکس ساعت'
        verbose_name_plural = 'عکس های ساعت'


class PriceChangeVariantModel(models.Model):
    variant = models.ForeignKey(WatchVariantModel, on_delete=models.CASCADE, related_name='rel_variant_price_chart')
    price = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.price)

    @property
    def fa_date(self):
        return datetime2jalali(self.date).strftime('%Y/%m/%d')

    class Meta:
        verbose_name = 'قیمت'
        verbose_name_plural = 'تغییرات قیمت'


class WatchSeenModel(models.Model):
    watch = models.ForeignKey(WatchModel, on_delete=models.CASCADE)
    ip = models.CharField(max_length=300)
    user = models.ForeignKey(CostumeUserModel, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دیده شدن'
        verbose_name_plural = 'دیده شدن های ساعت'


class CommentModel(models.Model):
    user = models.ForeignKey(CostumeUserModel, on_delete=models.CASCADE)
    product = models.ForeignKey(WatchModel, on_delete=models.CASCADE)
    reply = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='rel_replies')
    is_reply = models.BooleanField(default=False)
    can_show = models.BooleanField(default=False)
    text = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
