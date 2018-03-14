from __future__ import absolute_import, unicode_literals
from celery import task
from .models import Project, ProjectObject, SystemValues

from gdrive_api import gdriveAPI

@task()
def task_number_one():
    print('----------------------------------------')
    print('Время пришло расставить все по местам!')
    print('----------------------------------------')

    if SystemValues.objects.count() < 1:
        return
    else:
        sys_val = SystemValues.objects.all()[0]

    gdrive = gdriveAPI()
    if not sys_val.changes_token:
        sys_val.changes_token = gdrive.get_start_changes_token()

    changes, new_start_page_token = gdrive.get_changes(sys_val.changes_token)
    if new_start_page_token:
        sys_val.changes_token = new_start_page_token

    for change in changes:
        try:
            pobject = ProjectObject.objects.get(main_file=change.get('fileId'))
            print('today, bitch!')
        except ProjectObject.DoesNotExist:
            print('Not today, bitch!')
    sys_val.save()
