import datetime
import random
from django.shortcuts import redirect, render
from django.views import View
from .forms import UserRegisterForm, OtpCodeForm, LoginForm, ChangeProfileForm
from .models import OtpCode, CostumeUserModel
import utils
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.urls import reverse_lazy
from order.cart import CART_SESSION_ID
from django.contrib.auth.forms import PasswordChangeForm


class UserRegisterView(View):
    form_class = UserRegisterForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'شما در حال حاظر در سایت وارد شده اید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        signup_form = self.form_class(request.POST)
        if signup_form.is_valid():
            cd = signup_form.cleaned_data
            rand_code = random.randint(100000, 999999)
            if OtpCode.objects.filter(phone=cd['phone']).exists():
                OtpCode.objects.filter(phone=cd['phone']).delete()
            OtpCode.objects.create(phone=cd['phone'], code=rand_code)
            utils.send_otp_code(cd['phone'], f'کد ثبت نام: {rand_code}')

            request.session['user_register_info'] = {
                'phone': cd['phone'],
                'email': cd['email'],
                'f_name': cd['f_name'],
                'l_name': cd['l_name'],
                'password': cd['password_1'],
                'is_otp_send': True,
            }
            messages.success(request, f'کد ثبت نام به صورت پیامک به شما ارسال شد', 'msg-bg-success')
            return redirect('product:products')

        # the form that checked validation will be handled with js ( it's just used for show to user not django )
        messages.error(request, 'اطلاعات وارد شده را لطفا اصلاح کنید', 'msg-bg-danger')
        return redirect('product:products')


class VerifyCodeView(View):
    form_class = OtpCodeForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'شما در حال حاظر در سایت وارد شده اید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        user_session = request.session['user_register_info']
        otp_instance = get_object_or_404(OtpCode, phone=user_session['phone'])
        verify_code_form = OtpCodeForm(request.POST)
        if verify_code_form.is_valid():
            user_code = verify_code_form.cleaned_data['code']
            if user_code != otp_instance.code:
                messages.warning(request, 'لطفا کد را به درستی وارد نمایید', 'msg-bg-warning')
                return redirect('product:products')
            otp_exp = otp_instance.created + datetime.timedelta(minutes=2)
            now = datetime.datetime.now().astimezone(otp_exp.tzinfo)
            if otp_exp < now:
                otp_instance.delete()
                del request.session['user_register_info']
                messages.warning(request, 'متاسفانه کد شما منقضی شده است دوباره در سایت ثبت نام نمایید', 'msg-bg-warning')
                return redirect('product:products')
            CostumeUserModel.objects.create_user(
                f_name=user_session['f_name'],
                l_name=user_session['l_name'],
                phone=user_session['phone'],
                email=user_session['email'],
                password=user_session['password'],
            )
            user = authenticate(request, username=user_session['phone'], password=user_session['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f'به سایت ما خوش آمدید:  {request.user.f_name} {request.user.l_name}', 'msg-bg-success')
            else:
                messages.warning(request, f'اطلاعات وارد شده اشتباه است لطفا دوباره امتحان کنید', 'msg-bg-danger')
            try:
                del request.session['user_register_info']
            except KeyError:
                pass
            otp_instance.delete()
            return redirect('product:products')
        return redirect('product:products')


class CancelSignupView(View):
    def get(self, request):
        try:
            del request.session['user_register_info']
            get_object_or_404(OtpCode, phone=request.session['user_register_info']['phone']).delete()
            messages.info(request, f'عضویت در سایت لغو شد', 'msg-bg-info')
        except KeyError:
            try:
                del request.session['user_register_info']
            except KeyError:
                pass
        return redirect('product:products')


class LoginView(View):

    # this will send user to home page if it wants to login again by url
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "شما در حال حاظر در سایت وارد شده اید", 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    # this will send user to home page if it wants to login by url
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "لطفا از طریق navbar وارد ثایت شوید", 'msg-bg-danger')
            return redirect('product:products')

    # authenticate user if it wants to login in correct way
    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            cd = login_form.cleaned_data
            user = authenticate(request, username=cd['phone'], password=cd['password'])
            if user is not None:
                login(request, user)
                messages.success(request, f'سلام دوباره {request.user.f_name} {request.user.l_name}', 'msg-bg-success')
            else:
                messages.error(request, 'اطلاعات وارد شده اشتباه است', 'msg-bg-danger')
        return redirect('product:products')


class LogoutView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "شما قبلا از سایت خارج شده اید", 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        carts = request.session.get(CART_SESSION_ID)
        logout(request)
        if carts:
            request.session[CART_SESSION_ID] = carts
        messages.success(request, 'خدانگهدار', 'msg-bg-info')
        return redirect('product:products')


class UserPasswordResetView(PasswordResetView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'شما در حال حاظر وارد سایت شده اید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    template_name = 'accounts/reset_password/reset_password_form.html'
    success_url = reverse_lazy('accounts:reset_done')
    email_template_name = 'accounts/reset_password/email_template.html'


class UserPasswordResetDoneView(PasswordResetDoneView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'شما در حال حاظر در سایت وارد شده اید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        messages.success(request,
                         'لینک تعویض رمز به شما ارسال گردید لطفا بخش spam ایمیل خود را چک کنید',
                         'msg-bg-success')
        return redirect('product:products')


class UserPasswordResetConfirmView(PasswordResetConfirmView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'شما در حال حاظر در سایت وارد شده اید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    template_name = 'accounts/reset_password/reset_confirm.html'
    success_url = reverse_lazy('accounts:reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'شما در حال حاظر در سایت وارد شده اید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        messages.success(request, 'رمز عبور با موفقیت تغییر یافت', 'msg-bg-success')
        return redirect('product:products')


class BookmarkView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'قبل از ورود به این بخش باید در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'bookmark_cards': request.user.rel_bookmarks.all(),
            'is_bookmark_page': True
        }
        return render(request, 'accounts/profile/profile.html', context)


class ShowChangeProfileView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'قبل از ورود به این بخش باید در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'is_change_profile_page': True
        }
        return render(request, 'accounts/profile/profile.html', context)


class ChangePasswordView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'قبل از ورود به این بخش باید در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        change_pass_form = PasswordChangeForm(request.user, request.POST)
        if change_pass_form.is_valid():
            change_pass_form.save()
            update_session_auth_hash(request, change_pass_form.user)
            messages.success(request, 'رمز شما با موفقیت تغییر یافت', 'msg-bg-success')
            return redirect('order:show_order')
        messages.success(request, 'لطفا رمز خود را به درستی وارد کنید')
        return redirect('accounts:show_change_profile')


class ChangeProfileView(View):
    form_class = ChangeProfileForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'برای ورود به این بخش باید در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        change_profile_form = self.form_class(request.POST)
        if change_profile_form.is_valid():
            cd = change_profile_form.cleaned_data
            if CostumeUserModel.objects.filter(phone=cd['phone']).exists():
                messages.warning(request, 'این شماره تلفن قبلا در سایت ثبت نام کرده است', 'msg-bg-warning')
                return redirect('accounts:show_change_profile')
            elif CostumeUserModel.objects.filter(email=cd['email']).exists():
                messages.warning(request, 'این آدرس ایمیل قبلا در سایت ثبت نام کرده است', 'msg-bg-warning')
                return redirect('accounts:show_change_profile')
            else:
                user = CostumeUserModel.objects.filter(phone=request.user.phone).first()
                user.f_name = cd['f_name']
                user.l_name = cd['l_name']
                user.phone = cd['phone']
                user.email = cd['email']
                user.postal_code = cd['postal_code']
                user.address = cd['address']
                user.save()
                messages.success(request, 'اطلاعات شما با موفقیت به روزرسانی شد', 'msg-bg-success')
        return redirect('accounts:show_change_profile')


class OtpDeleteUserView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت ثبت نام کنید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        rand_code = random.randint(100000, 999999)
        if OtpCode.objects.filter(phone=request.user.phone).exists():
            OtpCode.objects.filter(phone=request.user.phone).delete()
        OtpCode.objects.create(phone=request.user.phone, code=rand_code)
        utils.send_otp_code(request.user.phone, f'کد حذف حساب: {rand_code}')
        messages.success(request, f'کد حذف حساب به صورت پیامک به شما ارسال شد', 'msg-bg-success')
        return redirect('accounts:delete_user')


class DeleteUserView(View):
    form_class = OtpCodeForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'لطفا قبل از ورود به این بخش در سایت وارد شوید', 'msg-bg-danger')
            return redirect('product:products')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
        }
        return render(request, 'accounts/profile/incs/delete_account.html', context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            otp_code = get_object_or_404(OtpCode, phone=request.user.phone).code
            if code != otp_code:
                messages.error(request, 'کد وارد شده نادرست است لطفا کد را مجدد وارد کنید', 'msg-bg-danger')
                return redirect('order:show_order')
            else:
                CostumeUserModel.objects.filter(phone=request.user.phone).filter().delete()
                messages.success(request, 'حساب شما با موفقیت حذف شد   خدانگهدار :)', 'msg-bg-success')
                return redirect('product:products')
        context = {
            'form': form,
        }
        return render(request, 'accounts/profile/incs/delete_account.html', context)
