from .models import Semester

from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


def current_semester():
    return Semester.objects \
        .order_by('-start_date', ) \
        .filter(start_date__lte=datetime.today())[0]


def agreement_semester():
    return Semester.objects.order_by('-start_date')[0]


class EmailBackend(ModelBackend):
    def authenticate(self, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        else:
            if getattr(user, 'is_active', False) and user.check_password(password):
                return user
        return None