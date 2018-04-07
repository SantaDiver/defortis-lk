from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from parea.models import Project, ProjectObject, SystemValues, Contact
from django.shortcuts import get_object_or_404
from django.http import HttpResponseServerError
from celery.result import AsyncResult
from django.views.generic import View
from django.utils.decorators import method_decorator
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404
import os

from gdrive_api import gdriveAPI
from tasks import sync_main_file_task, upload_to_disk_task, delete_file_task
from .utils import tables_list, file_types_in_structure

# Create your views here.
def check_permissions(func):
    def func_wrapper(self, request, prj_object_id, *args, **kwargs):
        prj_object = get_object_or_404(ProjectObject, id=prj_object_id)
        prj = prj_object.project
        if not request.user in prj.allowed_users.all() or not request.user.is_active:
            return HttpResponseForbidden()
        if not request.user.is_staff:
            return HttpResponseForbidden()
        if SystemValues.objects.count() < 1:
            return HttpResponseServerError()
        return func(self, request, prj_object_id, *args, **kwargs)
    return func_wrapper

# @method_decorator(csrf_exempt, name='dispatch')
@method_decorator(login_required, name='dispatch')
class SyncView(View):
    @check_permissions
    def get(self, request, prj_object_id, *args, **kwargs):
        prj_object = get_object_or_404(ProjectObject, id=prj_object_id)
        prj = prj_object.project
        # if prj_object.sync_task_id:
        #     return HttpResponse('Synceing', status=201)
        # if not prj_object.synced:
        #     return HttpResponse('Has changes', status=202)
        # return HttpResponse('Synced', status=200)

        self.post(request, prj_object_id, *args, **kwargs)
        return redirect('gpr', prj.id)

    @check_permissions
    def post(self, request, prj_object_id, *args, **kwargs):
        prj_object = get_object_or_404(ProjectObject, id=prj_object_id)
        prj = prj_object.project
        if prj_object.synced:
            return HttpResponseForbidden('Already synced!')
        if prj_object.sync_task_id:
            return HttpResponseForbidden('Already synceing!')
        if not prj_object.main_file:
            return HttpResponseForbidden('No main file given!')

        id = sync_main_file_task.delay(prj_object_id)
        prj_object.sync_task_id = id
        prj_object.save()

        return HttpResponse(status=200)

@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'parea/login.html')

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/')

        return render(request, 'parea/login.html')

def log_user_out(request):
    logout(request)
    return redirect('login')

@login_required
def default_redirect(request):
    projects = Project.objects.filter(allowed_users__id__exact=request.user.id)
    if not projects:
        return HttpResponseForbidden()

    id = projects[0].id
    return redirect('%s/gpr' % id)

def eject_data_by_prj(func):
    def func_wrapper(request, selected_project_id, file_type=None):
        projects = Project.objects.filter(allowed_users__id__exact=request.user.id)
        selected_project = get_object_or_404(Project, id=selected_project_id)
        if not selected_project in projects:
            return HttpResponseForbidden()
        prj_objects = ProjectObject.objects.filter(project=selected_project)
        contacts = Contact.objects.filter(projects__id__exact=selected_project.id)
        if not file_type:
            return func(
                request,
                selected_project_id,
                projects,
                selected_project,
                prj_objects,
                contacts
            )
        else:
            return func(
                request,
                selected_project_id,
                file_type,
                projects,
                selected_project,
                prj_objects,
                contacts
            )
    return func_wrapper

@login_required
@eject_data_by_prj
def gpr(request, selected_project_id, projects, selected_project, prj_objects, \
    contacts):
    selected_project_name = selected_project.name
    return render(request, 'parea/gpr.html', {
        'projects' : projects,
        'contacts' : contacts,
        'selected_project_id' : selected_project_id,
        'selected_project_name' : selected_project_name,
        'uri' : 'gpr',
        'prj_objects' : prj_objects,
        'tables_list' : tables_list
    })

@login_required
@eject_data_by_prj
def talks(request, selected_project_id, projects, selected_project, prj_object, \
    contacts ):
    selected_project_name = selected_project.name
    return render(request, 'parea/talks.html', {
        'projects' : projects,
        'contacts' : contacts,
        'selected_project_id' : selected_project_id,
        'selected_project_name' : selected_project_name,
        'uri' : 'talks',
        'selected_project' : selected_project,
        'file_type' : 'Совещания',
    })

@login_required
@eject_data_by_prj
def documents(request, selected_project_id, projects, selected_project, prj_objects, \
    contacts ):
    selected_project_name = selected_project.name
    return render(request, 'parea/talks.html', {
        'projects' : projects,
        'contacts' : contacts,
        'selected_project_id' : selected_project_id,
        'selected_project_name' : selected_project_name,
        'uri' : 'documents',
        'selected_project' : selected_project,
        'file_type' : 'Документы',
    })

@login_required
@eject_data_by_prj
def information(request, selected_project_id, projects, selected_project, prj_objects, \
    contacts ):
    selected_project_name = selected_project.name
    return render(request, 'parea/talks.html', {
        'projects' : projects,
        'contacts' : contacts,
        'selected_project_id' : selected_project_id,
        'selected_project_name' : selected_project_name,
        'uri' : 'information',
        'selected_project' : selected_project,
        'file_type' : 'Информация',
    })

@login_required
@eject_data_by_prj
def photo(request, selected_project_id, projects, selected_project, prj_objects, \
    contacts ):
    selected_project_name = selected_project.name
    return render(request, 'parea/photo.html', {
        'projects' : projects,
        'contacts' : contacts,
        'selected_project_id' : selected_project_id,
        'selected_project_name' : selected_project_name,
        'uri' : 'photo',
    })

def handle_uploaded_file(f, file_path):
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

@login_required
@eject_data_by_prj
def upload_file(request, selected_project_id, file_type, projects, selected_project, \
    prj_objects, contacts):
    if not file_type in file_types_in_structure:
        raise Http404('Bad file type!')
    uploaded_file = request.FILES['file']
    file_name = uploaded_file.name
    file_path = os.path.join(settings.BASE_DIR, file_name)
    handle_uploaded_file(uploaded_file, file_path)

    upload_to_disk_task(
        request.user.id,
        file_path,
        file_name,
        selected_project_id,
        file_type
    )

    return redirect(('/%s/%s') % (selected_project_id, file_type))

@login_required
@eject_data_by_prj
def delete_file(request, selected_project_id, file_type, projects, selected_project, \
    prj_objects, contacts):
    if not request.user.is_staff:
        return HttpResponseForbidden()
    if not file_type in file_types_in_structure:
        raise Http404('Bad file type!')
    if not 'file_id' in request.GET:
        raise Http404('file id needed')
    file_id = request.GET['file_id']

    files = selected_project.files_structure[file_type]
    files = [x for x in files if x['id'] != file_id]
    selected_project.files_structure[file_type] = files
    selected_project.save()

    delete_file_task.delay(file_id)

    return redirect(('/%s/%s') % (selected_project_id, file_type))

@login_required
@eject_data_by_prj
def download_file(request, selected_project_id, file_type, projects, selected_project, \
    prj_objects, contacts):
    if not file_type in file_types_in_structure:
        raise Http404('Bad file type!')
    if not 'file_id' in request.GET:
        raise Http404('file id needed')
    file_id = request.GET['file_id']

    files = selected_project.files_structure[file_type]
    for file in files:
        if file['id'] == file_id:
            file['was_downloaded'] = True
    selected_project.files_structure[file_type] = files
    selected_project.save()

    return HttpResponse(200)
