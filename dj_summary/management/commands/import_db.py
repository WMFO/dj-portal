import MySQLdb
from dj_summary.models import Profile, SpinitronProfile, current_semester
from django.contrib.auth.models import User
import random, string


from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Import users from old database'

    def handle(self, *args, **options):
        db = MySQLdb.connect("localhost","dj_info","dj_info","dj_info")

        cursor = db.cursor()

        cursor.execute("SELECT * FROM DJ")

        djs = cursor.fetchall()

        for dj in djs:
            djo = {
                'id' : dj[0],
                'first_name' : dj[1],
                'last_name' : dj[2],
                'year_joined' : dj[3],
                'seniority_offset' : dj[4],
                'email' : dj[5],
                'phone' : dj[6],
                'student_id' : dj[7],
                'relationship' : dj[8],
                'access' : dj[9],
                'exec' : dj[10],
                'active' : dj[11],
                'middle_name' : dj[12],
                'nick_name' : dj[13],
                'sub' : dj[14],
                'unsubscribed' : dj[15],

            }
            if djo['email']:
                key = ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(50))
                try:
                    user = User.objects.create_user(djo['email'],djo['email'])
                    user.first_name = djo['first_name']
                    user.last_name = djo['last_name']
                    user.is_staff = (djo['exec'] == 'yes')
                    user.save()

                    Profile.objects.create(user=user,
                                           nick_name=djo['nick_name'],
                                           date_joined=str(djo['year_joined']) + '-01-01',
                                           seniority_offset=djo['seniority_offset'],
                                           phone=djo['phone'],
                                           student_id=djo['student_id'],
                                           access=djo['access'][0],
                                           exec=(djo['exec'] == 'yes'),
                                           relationship=djo['relationship'][0],
                                           active=False,
                                           key=key,
                                           semester_joined=current_semester()
                                           )
                    self.stdout.write("Added " + djo['first_name'] + " " + djo['last_name'])
                    try:
                        SpinitronProfile.objects.get(spinitron_email=djo['email'])
                    except:
                        self.stderr.write("Spinitron user not found for " + djo['first_name'] + ' ' + djo['last_name'])
                except:
                    self.stderr.write("Exception creating " + djo['first_name'] + " " + djo['last_name'])