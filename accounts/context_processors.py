from .forms import UserRegisterForm, OtpCodeForm, LoginForm


def cp_signup(request):
    return {
        'signup_form': UserRegisterForm(),
    }


def cp_verify_code(request):
    try:
        if request.session['user_register_info']['is_otp_send']:
            return {
                'verify_code_form': OtpCodeForm(),
            }
    except KeyError:
        return {}


def cp_login(request):
    return {
        'login_form': LoginForm(),
    }
