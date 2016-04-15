from .models import Semester

from datetime import datetime


def current_semester():
    return Semester.objects \
        .order_by('-start_date', ) \
        .filter(start_date__lte=datetime.today())[0]


def agreement_semester():
    return Semester.objects.order_by('-start_date')[0]

