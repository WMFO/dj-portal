from django.conf.urls import patterns, url
from . import views

urlpatterns = patterns('',
    url(r'^login/$',
        views.formlogin,
        name='login',
    ),
    url(
        r'^logout/$',
        'django.contrib.auth.views.logout',
        name='logout',
    ),
)