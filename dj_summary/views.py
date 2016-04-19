from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render
import json
from dj_summary import utilities
from .models import Agreement, Timeslot, Profile, SpinitronProfile
from django.contrib.auth.models import User


@login_required
def index(request):
    #Volunteer.objects.filter(pk=request.user.id)
    profile = request.user.profile
    current_semester = utilities.current_semester()
    agreement_semester = utilities.agreement_semester()

    # get this semester's volunteering
    volunteer_entries = request.user.volunteer_set.filter(semester=current_semester.id)

    # get total volunteering this semester
    volunteering_this_semester = {
        'total' : profile.volunteer_hours_total,
        'subbing' : profile.volunteer_hours_subbing,
        'regular' : profile.volunteer_hours_regular,
    }
    volunteering_total = request.user.volunteer_set.aggregate(Sum(F('number_of_hours')))

    user = request.user
    profile = request.user.profile

    shows_query = request.user.show_set.filter(timeslot__semester=current_semester.id)
    shows = []
    for show in shows_query:
        shows.append({
            'name' : show.name,
            'assignments' : show.assignment_set.all(),
            'timeslot' : show.timeslot_set.filter(semester=current_semester.id)[0],
        })
    agreement_shows = user.show_set.filter(timeslot__semester=agreement_semester).all()
    schedule_requested = True if agreement_shows\
        else False

    #todo: this not working?
    scheduled = True if agreement_shows.filter(timeslot__accepted=True,timeslot__semester=agreement_semester)\
        .all() else False

    agreement = True if user.agreement_set.filter(semester=agreement_semester).all() else False
    data = {
        'volunteer_entries' : volunteer_entries,
        'volunteering_this_semester' : volunteering_this_semester,
        'total_volunteering' : volunteering_total["number_of_hours__sum"],
        'profile' : profile,
        'user' : request.user,
        'current_semester' : current_semester,
        'shows': shows,
        'checklist': {
            'agreement':agreement,
            'volunteering':profile.volunteering_completed,
            'schedule_requested':schedule_requested,
            'scheduled':scheduled,
        },
        'next_semester': agreement_semester,
    }
    return render(request, 'dj_summary/index.html', data)
    #HttpResponse("You volunteered %s" % (profile.student_id))

def agreement(request):
    agreement_semester = utilities.agreement_semester()
    current_agreement = request.user.agreement_set.filter(user__agreement__semester_id=agreement_semester.id)
    if not current_agreement:
        data = {
            'semester' : agreement_semester.name,
        }
        if (request.method == "POST"):
            a = Agreement.objects.create(user_id=request.user.id, semester_id=agreement_semester.id)
            a.signature = request.POST['signature']
            a.save()
            return HttpResponseRedirect(reverse('schedule'))
        return render(request, 'dj_summary/agreement.html', data)
    else:
        return HttpResponseRedirect(reverse('schedule'))

def choose_show(request):
    return HttpResponse("Use this page to select a show")

def schedule(request):
    # todo: make this user selectable
    show = request.user.show_set.all()[0]

    agreement_semester = utilities.agreement_semester()
    current_agreement = request.user.agreement_set.filter(user__agreement__semester_id=agreement_semester.id)
    if not current_agreement:
        return HttpResponseRedirect(reverse('agreement'))
    scheduled = show.timeslot_set.filter(semester_id=agreement_semester,accepted=True)
    if scheduled:
        return HttpResponse("Your show has been scheduled already by the PD for the current semester. Please contact the PD if you'd like to change show times.")

    try:
        last_semester = show.timeslot_set.filter(accepted=True)[0].semester.name
    except:
        last_semester = False
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    data = {
        'show': show,
        'last_semester': last_semester,
        'semester': agreement_semester.name,
    }

    return render(request, 'dj_summary/schedule.html', data)


def schedule_api(request):
    agreement_semester = utilities.agreement_semester()
    #todo: define permission for show scheduling (was assigned last semester show was scheduled)
    #todo: allow user to specify show
    show = request.user.show_set.all()[0]
    if request.method == "POST":
        show.timeslot_set.filter(semester=agreement_semester,accepted=False).delete()
        #return HttpResponse(request.body)
        body_unicode = request.body.decode('utf-8')
        data = json.loads(body_unicode)
        for counter, slot in enumerate(data['slots']):
            timeslot = Timeslot.objects.create(priority=counter,
                                               length=data['length'],
                                               show=show,
                                               semester=agreement_semester,
                                               alternating=data['alternating'],
                                               slot=slot['cell'])
            timeslot.save()
        return HttpResponse("Success")
    else:   

        current_shows = Timeslot.objects.filter(accepted=True,semester_id=agreement_semester.id)
        slots = []
        for s in current_shows:
            for i in range(s.slot,s.slot + s.length ):
                slots.append(i)

        #todo: adjust to be user selectable
        user_slots = request.user.show_set\
            .order_by('-timeslot__semester__start_date')[0]\
            .timeslot_set.filter(semester_id=agreement_semester.id)\
            .order_by("priority").all()
        user_slots_json = []
        for u in user_slots:
            user_slots_json.append({
                'cell' : u.slot,
                'length' : u.length,
                'weekday' : u.weekday,
                'day' : u.weekday_int,
                'hour' : u.hour,
                'alternating' : u.alternating,
            })
        return JsonResponse({'schedule':'yes',
                             'scheduled_slots':slots,
                             'user_slots':user_slots_json,
                             })

def register(request,key=''):
    errors = []
    try:
        profile = Profile.objects.get(key=key)
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Invalid registration key")

    if (request.method == 'POST'):
        try:
            spinitron = SpinitronProfile.objects.get(spinitron_email=request.POST['spinitron_email'])
            profile.user.first_name = request.POST['first_name']
            profile.middle_name = request.POST['middle_name']
            profile.user.last_name = request.POST['last_name']
            profile.nick_name = request.POST['nick_name']
            profile.phone = request.POST['phone']
            profile.seniority_offset = request.POST['seniority_offset']
            profile.nick_name = request.POST['nick_name']
            profile.nick_name = request.POST['nick_name']
            profile.nick_name = request.POST['nick_name']

        except ObjectDoesNotExist as e:
            errors.append(e.args)
        #return HttpResponse("Nothing")

    try:
        spinitron = SpinitronProfile.objects.get(spinitron_email=profile.user.email)
    except ObjectDoesNotExist:
        spinitron = False



    data = {
        'first_name' : profile.user.first_name,
        'input_list' : [
            {'name' :'first_name',
            'data': profile.user.first_name,
             'friendly_name' : "First Name",},

            {'name': 'middle_name',
             'data': profile.middle_name,
             'friendly_name': "Middle Name",},

            {'name': 'last_name',
             'data': profile.user.last_name,
             'friendly_name': "Last Name",},

            {'name': 'nick_name',
             'data': profile.nick_name,
             'friendly_name': "Nickname",},

            {'name': 'student_id',
             'data': profile.student_id,
             'friendly_name': "Student ID Number",
             'help':"Community members enter n/a"},

            {'name': 'email',
             'data': profile.user.email,
             'friendly_name': "Email Address",
             'help':"Email address you will use to log in to the DJ Portal."},

            {'name': 'date_joined',
             'data': profile.date_joined,
             'friendly_name': "Date Joined",
             'help': 'The (approximate) date you joined WMFO',},

            {'name': 'phone',
             'data': profile.phone,
             'friendly_name': "Phone Number",},

            {'name': 'number_of_semesters',
             'data': profile.seniority_offset,
             'friendly_name': "Number of WMFO Seasons",},
        ],
        'read_only' : [
            {'name':'Relationship',
             'data':profile.get_relationship_display(),},
            {'name':'Executive Board',
             'data':profile.exec,},
            {'name':'Access Level',
             'data':profile.get_access_display(),},
        ],
        'spinitron' : spinitron,
        'errors' : errors,
    }
    return render(request,'dj_summary/register.html', data)