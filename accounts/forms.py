from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from .models import CostumeUserModel
from captcha.fields import ReCaptchaField


class CostumeUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label='password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='confirm password')

    class Meta:
        model = CostumeUserModel
        fields = ('f_name', 'l_name', 'phone', 'email')

    def clean(self):
        """
            to be sure that password has alpha & upper & numeric & slower with more than 8 character
        """
        cd = super().clean()
        password1 = cd.get('password1')
        password2 = cd.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError('passwords must be match')
        elif len(password1) < 8:
            raise ValidationError('password most be more than 8 characters')
        elif not any(i.isalpha() for i in password1):
            raise ValidationError('password most have at least one alpha character')
        elif not any(i.isupper() for i in password1):
            raise ValidationError('password must have at least one upper character')
        elif not any(i.isnumeric() for i in password1):
            raise ValidationError('password must have at least one number')
        elif not any(i.islower() for i in password1):
            raise ValidationError('password most have at least one slower character')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class CostumeUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text='forgot your password ? -> <a href="../password/">click here</a>')

    class Meta:
        model = CostumeUserModel
        fields = ('f_name', 'l_name', 'phone', 'email', 'address', 'password', 'last_login')


# ----------------------------------------------------- user register
class UserRegisterForm(forms.Form):
    f_name = forms.CharField(label='نام (انگلیسی) *', widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    l_name = forms.CharField(label='نام خانوادگی (انگلیسی) *', widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    phone = forms.CharField(label='شماره تماس *', widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    email = forms.EmailField(label='ایمیل', required=False,
                             widget=forms.EmailInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    password_1 = forms.CharField(label='رمز ورود (8حرف شامل عدد و حداقل یک حرف انگلیسی بزرگ) *',
                                 widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    password_2 = forms.CharField(label='تایید رمز ورود *',
                                 widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if CostumeUserModel.objects.filter(phone=phone).exists():
            raise ValidationError('this phone number has been registered before')
        return phone

    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if CostumeUserModel.objects.filter(email=email).exists():
                raise ValidationError('this email address has been registered before')
        return email

    def clean(self):
        cd = super().clean()
        password_1 = cd.get('password_1')
        password_2 = cd.get('password_2')
        if password_1 and password_2:
            if password_1 and password_2 and password_1 != password_2:
                raise ValidationError('passwords must be match')
            elif len(password_1) < 8:
                raise ValidationError('password most be more than 8 characters')
            elif not any(i.isalpha() for i in password_1):
                raise ValidationError('password most have at least one alpha character')
            elif not any(i.isupper() for i in password_1):
                raise ValidationError('password must have at least one upper character')
            elif not any(i.isnumeric() for i in password_1):
                raise ValidationError('password must have at least one number')
            elif not any(i.islower() for i in password_1):
                raise ValidationError('password most have at least one slower character')
        else:
            raise ValidationError('please add your password')


class OtpCodeForm(forms.Form):
    code = forms.IntegerField(label='کد تاییدی', widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))


class LoginForm(forms.Form):
    phone = forms.CharField(label='شماره تماس', widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    password = forms.CharField(label='رمز ورود', widget=forms.PasswordInput(attrs={'class': 'form-control bg-dark text-light responsive-5-2'}))
    captcha = ReCaptchaField()


# change account information
class ChangeProfileForm(forms.ModelForm):
    class Meta:
        model = CostumeUserModel
        fields = ('f_name', 'l_name', 'phone', 'email', 'postal_code', 'address')
