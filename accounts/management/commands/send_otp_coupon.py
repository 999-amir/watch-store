from django.core.management.base import BaseCommand
from accounts.models import CostumeUserModel
from utils import send_otp_code
from order.models import CouponModel


class Command(BaseCommand):
    help = 'this command will send sms to introduction new coupon code'

    def handle(self, *args, **options):
        code = str(input('what is the coupon code? ->'))
        coupon = CouponModel.objects.filter(coupon_code=code).first()
        number = int(input('how many ->'))
        users = CostumeUserModel.objects.filter(total_buy__gte=number)
        if coupon and users:
            users_length = len(users)
            i = 1
            for user in users:
                coupon.user.add(user)
                text = 'سلام خدمت' + str(user.l_name) + '\n' + 'کد تخفیف مخصوص افرادی که بیش از' + str(number) + 'محصول از ما خریداری کرده اند' + '\n'+ 'code: ' + str(coupon.coupon_code)
                send_otp_code(user.phone, text)
                print(f'({i}/{users_length}) name: {user.f_name}-{user.l_name} ----- phone:{user.phone} ==========> DONE')
                i += 1
        else:
            print('check out -> coupon, users')
        self.stdout.write('************** operation completed **************')
