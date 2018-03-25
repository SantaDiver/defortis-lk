from rest_framework import serializers

from parea.models import Project, ProjectObject

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'pk',
            'name'
        ]

class PrjObjectsSerializer(serializers.ModelSerializer):
    synceing = serializers.ReadOnlyField(source='get_synceing')

    class Meta:
        model = ProjectObject
        fields = [
            'pk',
            'name',
            'project',
            'files_structure',
            'synced',
            'synceing'
        ]
