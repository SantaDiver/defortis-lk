from django.conf.urls import url, include

from .views import SyncView, LoginView, log_user_out

urlpatterns = [
    url(r'^sync/(?P<prj_object_id>\d+)/$', SyncView.as_view(), name='sync'),
    url(r'^api/', include('parea.api.urls', namespace='api')),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', log_user_out, name='logout'),
]
