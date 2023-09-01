from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CostumeUserManager
from django.contrib.auth.models import PermissionsMixin


class CostumeUserModel(AbstractBaseUser, PermissionsMixin):
    f_name = models.CharField(max_length=200)
    l_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=11, unique=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    total_buy = models.PositiveIntegerField(default=0)

    objects = CostumeUserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ('f_name', 'l_name', 'email')

    # def has_perm(self, perm, obj=None):
    #     return True
    #
    # def has_module_perms(self, app_label):
    #     return True

    @property
    def is_staff(self):
        return self.is_admin

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'


# ----------------------------------------------------------- user reqister
class OtpCode(models.Model):
    phone = models.CharField(max_length=11)
    code = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.phone} - {self.code}'

    class Meta:
        verbose_name = 'کد ثبت نام'
        verbose_name_plural = 'کدهای ثبت نام'