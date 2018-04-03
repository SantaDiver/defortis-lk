from __future__ import absolute_import, unicode_literals
from celery import task
from parea.models import Project, ProjectObject, SystemValues
from pprint import pprint
from celery import Task
from datetime import datetime
import pytz
from django.conf import settings

from gdrive_api import gdriveAPI
from utils import versions_number

class BaseTask(Task):
    """Abstract base class for all tasks in my app."""

    abstract = True

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry at retry."""
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Log the exceptions to sentry."""
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

def backoff(attempts):
    """Return a backoff delay, in seconds, given a number of attempts.

    The delay increases very rapidly with the number of attemps:
    1, 2, 4, 8, 16, 32, ...

    """
    return 2 ** attempts

@task(
    bind=True,
    max_retries=3,
    soft_time_limit=60,
    base=BaseTask
)
def check_main_file_changes_task(self):
    if SystemValues.objects.count() < 1:
        returnpprint(versions_list[0])
    else:
        sys_val = SystemValues.objects.all()[0]

    gdrive = gdriveAPI()
    if not sys_val.changes_token:
        sys_val.changes_token = gdrive.get_start_changes_token()

    try:
        changes, new_start_page_token = gdrive.get_changes(sys_val.changes_token)
    except Exception as exc:
        self.retry(countdown=backoff(self.request.retries), exc=exc)
    if new_start_page_token:
        sys_val.changes_token = new_start_page_token
    sys_val.save()

    for change in changes:
        try:
            pobject = ProjectObject.objects.get(main_file=change.get('fileId'))
            pobject.synced = False
            pobject.save()
        except ProjectObject.DoesNotExist:
            pass

@task(
    bind=True,
    max_retries=3,
    soft_time_limit=60,
    base=BaseTask
)
def sync_main_file_task(self, prj_object_id):
    sys_val = SystemValues.objects.all()[0]
    gdrive = gdriveAPI()
    prj_object = ProjectObject.objects.get(id=prj_object_id)
    prj = prj_object.project

    files_structure = prj_object.files_structure
    if not 'graphs' in files_structure:
        files_structure['graphs'] = []
    graphs = files_structure['graphs']

    try:
        file_name = gdrive.get_file_by_id(prj_object.main_file)['name']
        if len(file_name.split('.')) < 2:
            file_name += 'xlsx'
        res, id = gdrive.split_main_file(prj_object, sys_val, file_name)
    except Exception as exc:
        self.retry(countdown=backoff(self.request.retries), exc=exc)
        return

    timezone = settings.TIME_ZONE
    now = datetime.now(pytz.timezone(timezone))
    res = {
        'timestamp' : now.timestamp(),
        'links' : res,
        'id' : id
    }
    if len(graphs) >= versions_number:
        print('--------------------------------------------------------')
        print([ graphs[-1]['id'] ])
        print('--------------------------------------------------------')

        gdrive.delete_files([ graphs[-1]['id'] ])
        graphs = graphs[-1:] + graphs[:-1]
        graphs[0] = res
    else:
        graphs = [res] + graphs

    files_structure['graphs'] = graphs
    prj_object.sync_task_id = None
    prj_object.synced = True

    sys_val.save()
    prj_object.save()

    return res
