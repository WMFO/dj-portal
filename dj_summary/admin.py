from django.contrib import admin

from .models import Show, Semester, Timeslot, Discipline, Volunteer, Profile, SpinitronProfile, Assignment

admin.site.register(Show)
admin.site.register(Semester)
admin.site.register(Timeslot)
admin.site.register(Discipline)
admin.site.register(Assignment)
admin.site.register(Volunteer)
admin.site.register(Profile)
admin.site.register(SpinitronProfile)