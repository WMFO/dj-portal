from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^agreement$', views.agreement, name='agreement'),
    url(r'^schedule$', views.schedule, name='schedule'),
    url(r'^scheduleapi$', views.schedule_api, name='schedule_api'),
    url(r'^register/(?P<key>.*)$', views.register,name='register'),
]