from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^agreement$', views.agreement, name='agreement'),
    url(r'^schedule/(?P<showid>.*)$', views.schedule, name='schedule'),
    url(r'^scheduleapi/(?P<showid>.*)$', views.schedule_api, name='schedule_api'),
    url(r'^register/(?P<key>.*)$', views.register,name='register'),
    url(r'^schedule_admin_api$', views.schedule_admin_api, name='schedule_admin_api'),
    url(r'^show_api$', views.show_api, name='show_api'),
    url(r'^login$', views.login, name='login'),
    url(r'^choose_show', views.choose_show, name='login'),
    url(r'^add_djs/(?P<showid>.*)$', views.add_djs, name='add_djs')
]