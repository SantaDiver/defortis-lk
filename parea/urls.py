from django.conf.urls import url, include

from .views import SyncView

urlpatterns = [
    url(r'^sync/(?P<prj_object_id>\d+)/$', SyncView.as_view(), name='sync'),
    url(r'^api/', include('parea.api.urls', namespace='api')),
]
