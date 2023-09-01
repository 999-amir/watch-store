from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as userbaseadmin
from .forms import CostumeUserCreationForm, CostumeUserChangeForm
from .models import CostumeUserModel, OtpCode
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date import datetime2jalali



class CostumeUserAdmin(ModelAdminJalaliMixin, userbaseadmin):
    form = CostumeUserChangeForm
    add_form = CostumeUserCreationForm
    list_display = ('f_name', 'l_name', 'phone', 'email', 'is_admin', 'total_buy')
    list_filter = ('is_admin',)
    fieldsets = (
        (
            'information',
            {'fields': ('f_name', 'l_name', 'phone', 'email', 'postal_code', 'address', 'password')}
        ),
        (
            'permissions',
            {'fields': ('is_active', 'is_admin', 'is_superuser', 'last_login', 'groups')}
        )
    )
    add_fieldsets = (
        (
            'information',
            {'fields': ('f_name', 'l_name', 'phone', 'email', 'password1', 'password2')}
        ),
    )
    search_fields = ('l_name', 'phone', 'email')
    ordering = ('l_name',)
    filter_horizontal = ('groups',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            form.base_fields['is_superuser'].disabled = True
        return form


# admin.site.unregister(Group)
admin.site.register(CostumeUserModel, CostumeUserAdmin)

def created(model):
    return datetime2jalali(model.created).strftime('%Y/%m/%d _ %H:%M:%S')

@admin.register(OtpCode)
class OtpCodeAdmin(admin.ModelAdmin):
    list_display = ('phone', 'code', created)
    list_filter = ('created',)
