from django.contrib.auth.models import BaseUserManager


class CostumeUserManager(BaseUserManager):
    def create_user(self, f_name, l_name, phone, password, email=None):
        if not phone:
            raise ValueError('please add your phone number :)')
        if not f_name:
            raise ValueError('please add your first name :)')
        if not l_name:
            raise ValueError('please add your last name :)')

        user = self.model(f_name=f_name, l_name=l_name, phone=phone, email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, f_name, l_name, phone, password, email=None):
        user = self.create_user(f_name, l_name, phone, password, email)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
