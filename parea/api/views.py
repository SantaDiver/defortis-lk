from rest_framework import generics
from parea.models import Project, ProjectObject
from .serializers import ProjectSerializer, PrjObjectsSerializer
from django.http import Http404
from rest_framework import status

class ProjectsListView(generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = ProjectSerializer
    # queryset = Project.objects.all()

    def get_queryset(self):
        return Project.objects.filter(allowed_users__id__exact=self.request.user.id)

    # def get_object(self):
    #     pk = self.kwargs.get('pk')
    #     return Project.objects.get(pk=pk)

class PrjObjectsListView(generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = PrjObjectsSerializer

    def get_queryset(self):
        projects = Project.objects.filter(allowed_users__id__exact=self.request.user.id)
        objects = []
        for project in projects:
            objects += ProjectObject.objects.filter(project=project)
        return objects


class PrjObjectsDetailView(generics.RetrieveAPIView):
    lookup_field = 'pk'
    serializer_class = PrjObjectsSerializer

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            obj = ProjectObject.objects.get(pk=pk)
            print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$')
            print(self.request.user in obj.project.allowed_users.all())
            print('#############################')
            if not self.request.user in obj.project.allowed_users.all():
                raise Http404
            else:
                return obj
        except:
            raise Http404
