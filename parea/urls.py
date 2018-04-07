from django.conf.urls import url, include
from django.views.generic import TemplateView
from .views import SyncView, LoginView, log_user_out, gpr, default_redirect, \
    talks, upload_file, delete_file, download_file, documents, information, photo

urlpatterns = [
    url(r'^sync/(?P<prj_object_id>\d+)/$', SyncView.as_view(), name='sync'),
    url(r'^api/', include('parea.api.urls', namespace='api')),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', log_user_out, name='logout'),
    url(r'^$', default_redirect, name='default_redirect'),
    url(r'^(?P<selected_project_id>\d+)/gpr/$', gpr, name='gpr'),
    url(r'^(?P<selected_project_id>\d+)/talks/$', talks, name='talks'),
    url(r'^(?P<selected_project_id>\d+)/documents/$', documents, name='documents'),
    url(r'^(?P<selected_project_id>\d+)/information/$', information, name='information'),
    url(r'^(?P<selected_project_id>\d+)/photo/$', photo, name='photo'),
    url(r'^(?P<selected_project_id>\d+)/(?P<file_type>\w+)/upload_file/$', upload_file, name='upload_file'),
    url(r'^(?P<selected_project_id>\d+)/(?P<file_type>\w+)/delete_file/$', delete_file, name='delete_file'),
    url(r'^(?P<selected_project_id>\d+)/(?P<file_type>\w+)/download_file/$', download_file, name='download_file'),
]
