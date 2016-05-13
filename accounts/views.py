from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden

from django.contrib.auth import authenticate, login

from .forms import LoginForm

def formlogin(request):
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
            user = authenticate(username=data['email_address'],password=data['password'])
            if user is not None:
                if not user.is_active:
                    errors.append("Your account is disabled. Email ops@wmfo.org")
            else:
                errors.append("Authentication error")

            if not errors:
                login(request,user)
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
    return render(request, 'accounts/login.html', data)
