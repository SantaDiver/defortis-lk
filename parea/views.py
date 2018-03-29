from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from parea.models import Project, ProjectObject, SystemValues
from django.shortcuts import get_object_or_404
from django.http import HttpResponseServerError
from celery.result import AsyncResult
from django.views.generic import View
from django.utils.decorators import method_decorator
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect


from gdrive_api import gdriveAPI
from tasks import sync_main_file_task

# Create your views here.
def check_permissions(func):
    def func_wrapper(self, request, prj_object_id, *args, **kwargs):
        prj_object = get_object_or_404(ProjectObject, id=prj_object_id)
        prj = prj_object.project
        if not request.user in prj.allowed_users.all() or not request.user.is_active:
            return HttpResponseForbidden()
        if SystemValues.objects.count() < 1:
            return HttpResponseServerError()
        return func(self, request, prj_object_id, *args, **kwargs)
    return func_wrapper

@method_decorator(csrf_exempt, name='dispatch')
# @method_decorator(login_required, name='dispatch')
class SyncView(View):
    @check_permissions
    def get(self, request, prj_object_id, *args, **kwargs):
        prj_object = get_object_or_404(ProjectObject, id=prj_object_id)
        prj = prj_object.project
        if prj_object.sync_task_id:
            return HttpResponse('Synceing', status=201)
        if not prj_object.synced:
            return HttpResponse('Has changes', status=202)
        return HttpResponse('Synced', status=200)

    # @check_permissions
    def post(self, request, prj_object_id, *args, **kwargs):
        prj_object = get_object_or_404(ProjectObject, id=prj_object_id)
        prj = prj_object.project
        if prj_object.synced:
            return HttpResponseForbidden('Already synced!')
        if prj_object.sync_task_id:
            return HttpResponseForbidden('Already synceing!')

        id = sync_main_file_task.delay(prj_object_id)
        prj_object.sync_task_id = id
        prj_object.save()

        return HttpResponse(status=200)

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
