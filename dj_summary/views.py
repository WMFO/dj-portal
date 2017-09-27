from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.shortcuts import render
import json
from dj_summary import utilities
from .models import Agreement, Timeslot, SpinitronProfile, Show, Assignment, User

from django.contrib.auth import login as auth_login
from dj_summary.utilities import EmailBackend
from .forms import RegisterForm, LoginForm, CreateShowForm


@login_required
def index(request):
    #Volunteer.objects.filter(pk=request.user.id)
    user = request.user
    current_semester = utilities.current_semester()
    agreement_semester = utilities.agreement_semester()

    # get this semester's volunteering
    volunteer_entries = request.user.volunteer_set.filter(semester=current_semester.id)

    # get total volunteering this semester
    volunteering_this_semester = {
        'total' : user.volunteer_hours_total,
        'subbing' : user.volunteer_hours_subbing,
        'regular' : user.volunteer_hours_regular,
    }
    volunteering_total = request.user.volunteer_set.aggregate(Sum(F('number_of_hours')))

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
        'user' : user,
        'current_semester' : current_semester,
        'shows': shows,
        'checklist': {
            'agreement':agreement,
            'volunteering':user.volunteering_completed,
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
        if request.method == "POST":
            a = Agreement.objects.create(user_id=request.user.id, semester_id=agreement_semester.id)
            a.signature = request.POST['signature']
            a.save()
            return HttpResponseRedirect(reverse('schedule'))
        return render(request, 'dj_summary/agreement.html', data)
    else:
        return HttpResponseRedirect(reverse('schedule'))

def choose_show(request):
    if request.method == 'POST':
        showid = request.POST['show-select']
        url = reverse('schedule', kwargs={'showid' : showid})
        return HttpResponseRedirect(url)

    shows = Show.objects.filter(assignment__djs=request.user).values()

    data = {
        'shows' : shows,
    }
    return render(request, 'dj_summary/choose_show.html', data)


def show_api(request):
    if request.method == 'GET':
        shows = request.user.show_set.all()

        show_list = []
        for s in shows:
            djs = [{'name': d.first_name + ' ' + d.last_name,
                    'id' : d.id} for d in s.djs]
            show_list.append({'name':s.name,
                              'id' : s.id,
                              'djs' : djs} )
        return JsonResponse(show_list)

    if request.method == 'POST':
        # assign DJs to
        # { 'djs' : [id1, id2, id3...], 'show' : { 'id' : show_id, 'name' : n, 'description' : d }
        d = json.loads(request.body.decode('utf-8'))
        agreement_semester = utilities.agreement_semester()

        show_id = -1

        if 'id' in d['show'].keys():
            s = Show.objects.find(id=d['show']['id'])
            show_id = s.id
        else:
            s = Show(name=d['show']['name'],description=d['show']['description'])
            s.save()


        Assignment(semester=agreement_semester.id,djs=request.user.id,show=show_id)

        #todo: secure this so I can only add djs if I've been in the show before


        #show = Show.objects.get(id=d['show_id'])
        for id in d['djs']:
            Assignment(semester=agreement_semester.id,djs=id,show=show_id).save()


def schedule(request,showid):
    # todo: make this user selectable
    show = Show.objects.get(id=showid)
    if not show.assignment_set.filter(djs=request.user).exists():
        return HttpResponse("Permission Denied")
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


def add_djs(request,showid):
    show = Show.objects.get(id=showid)
    if not show.assignment_set.filter(djs=request.user).exists():
        return HttpResponse("Permission Denied")
    if request.POST:
        return HttpResponse(request.POST.getlist("djs[]"))
    agreement_semester = utilities.agreement_semester()
    user_id = request.user.id
    show_user_ids = User.objects.filter(show=show).values_list('id',flat=True)
    users = User.objects.values('id','first_name','last_name')
    #
    #filter out current user from entry
    users_filtered = [x for x in users if x['id'] != user_id]
    show_user_ids_filtered = [x for x in show_user_ids if x != user_id]
    data = {
        'users' : users_filtered,
        'current_user_ids' : show_user_ids_filtered,
        'show' : show,
    }
    #return HttpResponse(data)
    return render(request,'dj_summary/add_djs.html',data)




def schedule_api(request, showid):
    agreement_semester = utilities.agreement_semester()
    #todo: define permission for show scheduling (was assigned last semester show was scheduled)
    #todo: allow user to specify show
    show = Show.objects.get(id=showid)
    if not show.assignment_set.filter(djs=request.user).exists():
        return HttpResponse("Permission Denied")

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

def calculate_show_rank(show,semester):
    # TODO: add rank formula
    # e.g.:
    # calculate_dj_rank(user_id,semester)
    # logic for 1 and 2 person shows
    return 1


def calculate_dj_rank(dj,semester):
    return 1


def schedule_admin_api(request):
    agreement_semester = utilities.agreement_semester()
    if request.method == 'GET':

        # Obtain all show IDs that have submitted scheduling slots for the current scheduling semester
        shows_to_be_scheduled = Timeslot.objects.filter(semester=agreement_semester)\
            .values('show_id').distinct()

        shows = []

        # Obtain show scheduling information
        for s in shows_to_be_scheduled:
            show_id = s['show_id']
            show = Show.objects.get(pk=show_id)

            #timeslots for show for semester
            timeslots = show.timeslot_set.filter(semester=agreement_semester).order_by('priority')
            length = timeslots[0].length
            alternating = timeslots[0].alternating

            #ain't that cute?
            timeslot_integers = [{'slot' : d.slot,
                                  'accepted' : d.accepted,
                                  'text' : d.text,
                                  'id' : d.id}

                                 for d in timeslots] #huzzah

            #get DJs
            djs = show.djs.only('first_name','last_name','id')

            dj_list = [{'first_name' : d.first_name,
                        'last_name' : d.last_name,
                        'id' : d.id, } for d in djs]

            shows.append({ 'show_id' : show.id,
                           'show_name' : show.name,
                           'rank' : calculate_show_rank(s['show_id'],agreement_semester),
                           'length' : length,
                           'djs' : dj_list,
                           'alternating' : alternating,
                           'timeslots' : timeslot_integers,
            })
        ordered_shows = sorted(shows,key= lambda x: x['rank'])

        return JsonResponse({'shows': ordered_shows,
                             })


def register(request,key=''):
    errors = []
    try:
        user = User.objects.get(key=key)
    except ObjectDoesNotExist:
        return HttpResponseForbidden("Invalid registration key")

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        try:
            if form.is_valid():
                data = form.cleaned_data
                if data['password'] != data['confirm_password']:
                    errors.append("Passwords must match")
                if len(data['password']) < 12:
                    errors.append("Password must be at least 12 characters long")

                spinitron = SpinitronProfile.objects.get(spinitron_email=request.POST['spinitron_email'])

                if not spinitron:
                    errors.append("Spinitron email does not match any known accounts")

                user.first_name = data['first_name']
                user.middle_name = data['middle_name']
                user.last_name = data['last_name']
                user.nick_name = data['nick_name']
                user.student_id = data['student_id']
                user.user.username = data['email']
                user.user.email = data['email']
                user.date_joined = data['date_joined']
                user.phone = data['phone']
                user.seniority_offset = data['number_of_semesters']
                if not errors:
                    user.set_password(data['password'])
                    user.save()
                    user.user.save()
                    return HttpResponseRedirect('/')

        except ObjectDoesNotExist as e:
            errors.append(e.args)
        #return HttpResponse("Nothing")

    try:
        spinitron = SpinitronProfile.objects.get(spinitron_email=user.email)
    except ObjectDoesNotExist:
        spinitron = False

    data = {
        'first_name': user.first_name,
        'middle_name': user.middle_name,
        'last_name': user.last_name,
        'nick_name': user.nick_name,
        'student_id': user.student_id,
        'email': user.user.email,
        'date_joined': user.date_joined,
        'phone': user.phone,
        'number_of_semesters': user.seniority_offset,
        'spinitron_email' : spinitron.spinitron_email,
    }

    try:
        form
        f = form
        f.password = ''
        f.confirm_password = ''
    except:
        f = RegisterForm(data)


    data = {
        'first_name': user.first_name,
        'read_only': [
            {'name': 'Relationship',
             'data': user.get_relationship_display(),},
            {'name': 'Executive Board',
             'data': user.exec,},
            {'name': 'Access Level',
             'data': user.get_access_display(),},
        ],
        'errors': errors,
        'form' : f,
    }

    return render(request,'dj_summary/register.html', data)


def login(request):
    errors = []
    if not hasattr(request.GET,'next'):
        next = '/'
    else:
        next = request.GET['next']

    if request.user.is_authenticated():
        return HttpResponseRedirect(next)

    if request.method == 'POST':
        f = LoginForm(request.POST)
        if f.is_valid():
            data = f.cleaned_data
            e = EmailBackend()
            user = e.authenticate(data['email_address'],data['password'])
            if user is not None:
                if not user.is_active:
                    errors.append("Your account is disabled. Email ops@wmfo.org")
            else:
                errors.append("Authentication error")

            if not errors:
                auth_login(request, user)
                return HttpResponseRedirect(next)

    try:
        f
        f.password = ''
    except:
        f = LoginForm()

    data = {
        'errors': errors,
        'form' :f,
    }
    return render(request, 'dj_summary/login.html', data)