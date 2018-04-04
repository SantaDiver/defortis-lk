from django.contrib import admin
from .models import Project, ProjectObject, SystemValues
from simple_history.admin import SimpleHistoryAdmin
from django import forms
from pprint import pprint
import sys
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget

sys.path.insert(0, './gdrive_api')
sys.path.insert(0, './parea')
from gdrive_api import gdriveAPI
# Register your models here.

@admin.register(Project)
class ProjectAdmin(SimpleHistoryAdmin):
    list_display = ('get_name',)
    search_fields = ('name',)

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget }
    }

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Название проекта'

class ProjectObjectForm(forms.ModelForm):
    class Meta:
        model = ProjectObject
        fields = '__all__'
        widgets = {
            'files_structure': PrettyJSONWidget(),
        }

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

@admin.register(ProjectObject)
class ProjectObjectAdmin(SimpleHistoryAdmin):
    form = ProjectObjectForm
    list_display = ('get_name',)
    search_fields = ('name',)

    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Название объекта'

@admin.register(SystemValues)
class SystemValuesAdmin(SimpleHistoryAdmin):
    list_display = ('get_name',)

    def get_name(self, obj):
        return 'Системные значения'
    get_name.short_description = 'Системные значения'
