from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, Sum


def current_semester():
    return Semester.objects \
        .order_by('-start_date', ) \
        .filter(start_date__lte=datetime.today())[0]


class Semester(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    def __str__(self):
        return self.name

class Show(models.Model):
    name = models.CharField(max_length=200)
    first_year = models.DateField()
    description = models.CharField(max_length=200)
    semesters = models.ManyToManyField(Semester,through='Timeslot')
    djs = models.ManyToManyField(User, through='Assignment')
    def __str__(self):
        return self.name

class Assignment(models.Model):
    show = models.ForeignKey(Show)
    djs = models.ForeignKey(User)
    semester = models.ForeignKey(Semester)
    def __str__(self):
        return self.show.name + ' - ' + self.semester.name


class Timeslot(models.Model):
    WEEKDAY_OPTIONS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    slot = models.IntegerField(default=-1)
    priority = models.IntegerField()
    length = models.IntegerField()
    alternating = models.BooleanField(default=False)
    show = models.ForeignKey(Show)
    accepted = models.BooleanField(default=False)
    semester = models.ForeignKey(Semester)

    @property
    def weekday(self):
        return self.WEEKDAY_OPTIONS[int(self.weekday_int)]

    @property
    def weekday_int(self):
        return self.slot // 24

    @property
    def hour(self):
        return self.slot % 24

    @property
    def end_hour(self):
        return (self.slot + self.length) % 24

    def set_slot(self, weekday, start_hour):
        try:
            i_weekday = int(weekday)
        except:
            for i, w in enumerate(self.WEEKDAY_OPTIONS):
                if self.WEEKDAY_OPTIONS[i].lower() == weekday.lower():
                    i_weekday = i
                    break
        self.slot = int(i_weekday % 7) + int(start_hour)


    @property
    def formatted(self):
        qualifier = '' if self.accepted else '(requested) '
        return qualifier + str(self.WEEKDAY_OPTIONS[self.weekday_int]) + ' ' + str(self.hour) + '-' + str(self.end_hour) + ':00'

    def __str__(self):
        qualifier = '' if self.accepted else '(requested) '
        return qualifier + str(self.WEEKDAY_OPTIONS[self.weekday_int]) + ' ' + str(self.hour) + '-' + str(self.end_hour) + ':00 @ ' + self.semester.name

class Agreement(models.Model):
    signature_date = models.DateTimeField(default=datetime.now())
    signature = models.CharField(max_length=100)
    user = models.ForeignKey(User)
    semester = models.ForeignKey(Semester)
    def __str__(self):
        return self.signature

class Discipline(models.Model):
    subject = models.CharField(max_length=200)
    incident_date = models.DateField()
    description = models.TextField()
    def __str__(self):
        return self.subject

class Volunteer(models.Model):
    subject = models.CharField(max_length=200)
    volunteer_date = models.DateField()
    semester = models.ForeignKey(Semester)
    number_of_hours = models.DecimalField(decimal_places=2,max_digits=4)
    subbing = models.BooleanField(default=False)
    user = models.ForeignKey(User)
    def __str__(self):
        return self.subject

class SpinitronProfile(models.Model):
    ROLES = (
        ('N','New User'),
        ('U','User'),
        ('E','Editor'),
        ('A','Admin'),
    )
    id = models.IntegerField(unique=True,primary_key=True)
    spinitron_name = models.CharField(max_length=150)
    dj_name = models.CharField(max_length=150)
    spinitron_email = models.CharField(max_length=150)
    role = models.CharField(max_length=1,choices=ROLES)
    def __str__(self):
        return str(self.id) + " - " + self.spinitron_name

class Profile(models.Model):
    RELATIONSHIPS = (
        ('S', 'Student'),
        ('A', 'Alum'),
        ('C', 'Community'),
    )
    ACCESSES = (
        ('G','General'),
        ('M','Music Department'),
        ('E','Engineer'),
        ('A','All'),
    )
    nick_name = models.CharField(max_length=75)
    middle_name = models.CharField(max_length=75)
    semester_joined = models.ForeignKey(Semester)
    seniority_offset = models.IntegerField()
    phone = models.CharField(max_length=15)
    student_id = models.CharField(max_length=15)
    access = models.CharField(max_length=1,choices=ACCESSES)
    exec = models.BooleanField()
    active = models.BooleanField()
    unsubscribe = models.BooleanField()
    sub = models.BooleanField()
    user = models.OneToOneField(User)
    relationship = models.CharField(max_length=1,choices=RELATIONSHIPS)
    spinitron = models.OneToOneField(SpinitronProfile,null=True)

    @property
    def volunteer_hours_regular(self):
        current_volunteer_entries = self.user.volunteer_set.filter(semester=current_semester().id)
        regular = current_volunteer_entries.filter(subbing=False)
        if regular:
            return regular.aggregate(Sum(F('number_of_hours')))['number_of_hours__sum']
        else:
            return 0

    @property
    def volunteer_hours_subbing(self):
        current_volunteer_entries = self.user.volunteer_set.filter(semester=current_semester().id)
        subbing = current_volunteer_entries.filter(subbing=True)
        if subbing:
            return subbing.aggregate(Sum(F('number_of_hours')))['number_of_hours__sum']
        else:
            return 0

    @property
    def volunteer_hours_total(self):
        current_volunteer_entries = self.user.volunteer_set.filter(semester=current_semester().id)
        if current_volunteer_entries:
            return current_volunteer_entries.aggregate(Sum(F('number_of_hours')))['number_of_hours__sum']
        else:
            return 0

    @property
    def volunteering_completed(self):
        return (self.volunteer_hours_total >= 5) and (self.volunteer_hours_regular >= 3)






