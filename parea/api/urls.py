from django.conf.urls import url, include

from .views import ProjectsListView, PrjObjectsListView, PrjObjectsDetailView
urlpatterns = [
    url(r'^projects/$', ProjectsListView.as_view(), name='projects-list'),
    url(r'^objects/$', PrjObjectsListView.as_view(), name='objects-list'),
    url(r'^objects/(?P<pk>\d+)/$', PrjObjectsDetailView.as_view(), name='object-detail'),
]
