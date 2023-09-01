from django.core.management.base import BaseCommand
from accounts.models import OtpCode
from datetime import datetime, timedelta
import pytz


class Command(BaseCommand):
    help = 'this command will delete all expired otp codes'

    def handle(self, *args, **options):
        exp_time = datetime.now(tz=pytz.timezone('Asia/Tehran')) - timedelta(minutes=2)
        OtpCode.objects.filter(created__lt=exp_time).delete()
        self.stdout.write('operation completed -> expired otp codes has been deleted')
