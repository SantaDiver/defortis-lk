from django.contrib import admin
from .models import Project, ProjectObject, SystemValues
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from pprint import pprint
import sys

sys.path.insert(0, './gdrive_api')
sys.path.insert(0, './parea')
from gdrive_api import gdriveAPI
# Register your models here.

@admin.register(Project)
class MyAdmin(SimpleHistoryAdmin):
    list_display = ('get_name',)
    search_fields = ('name',)

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Название проекта'

class ProjectObjectForm(forms.ModelForm):
    class Meta:
        model = ProjectObject
        fields = ['name', 'folder_id', 'project', 'main_file', 'list1_id',
            'list2_id', 'list3_id']

    def __init__(self, *args, **kwargs):
        super(ProjectObjectForm, self).__init__(*args, **kwargs)
        instance = self.instance
        gdrive = gdriveAPI()
        files = gdrive.get_folder_contents(instance.folder_id)
        self.fields['main_file'] = forms.ChoiceField(
            choices = [(file['id'], file['name']) for file in files]+
                [('', 'Не выбрано')],
            label = 'Основная таблица',
            required = False
        )

    def clean_main_file(self):
        if self.cleaned_data['main_file'] == "":
            return None
        else:
            return self.cleaned_data['main_file']

    def clean_list1_id(self):
        if self.cleaned_data['list1_id'] == "":
            return None
        else:
            return self.cleaned_data['list1_id']

    def clean_list2_id(self):
        if self.cleaned_data['list2_id'] == "":
            return None
        else:
            return self.cleaned_data['list2_id']

    def clean_list3_id(self):
        if self.cleaned_data['list3_id'] == "":
            return None
        else:
            return self.cleaned_data['list3_id']

@admin.register(ProjectObject)
class MyAdmin(SimpleHistoryAdmin):
    form = ProjectObjectForm
    list_display = ('get_name',)
    search_fields = ('name',)

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Название объекта'

@admin.register(SystemValues)
class MyAdmin(SimpleHistoryAdmin):
    list_display = ('get_name',)

    def get_name(self, obj):
        return 'Системные значения'
    get_name.short_description = 'Системные значения'
