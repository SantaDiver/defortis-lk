from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.dispatch import receiver
import sys
from pprint import pprint
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields import ArrayField
from tinymce.models import HTMLField

from .utils import root_folder_name, hidden_folder_name, photo_folder_name
sys.path.insert(0, './gdrive_api')
sys.path.insert(0, './parea')
from gdrive_api import gdriveAPI
# Create your models here.

class Project(models.Model):
    name = models.CharField(
        max_length=120,
        default='',
        unique=True,
        db_index=True,
        verbose_name='Название проекта'
    )
    folder_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name='ID Папки',
    )
    allowed_users = models.ManyToManyField(
        User,
        verbose_name='Допущены по API',
        blank=True
    )
    editor_users = ArrayField(
        models.CharField(
            max_length=50,
        ),
        blank=True,
        default=[],
        verbose_name='Допущены к Google Drive',
    )
    files_structure = JSONField(
        default={
            'talks' : [],
            'documents' : [],
            'information' : [],
        },
        blank=True,
        verbose_name='Структура файлов',
    )
    main_photo = models.ImageField(
        upload_to='parea/img/projects',
        height_field=None,
        width_field=None,
        max_length=100,
        default='',
        verbose_name='Основное фото проекта',
    )
    description = HTMLField(
        default='',
        verbose_name='Описание проекта',
    )

    history = HistoricalRecords()

    def __str__(self):
        return self.name

@receiver(models.signals.post_save, sender=Project)
def prj_call_save(sender, instance, created, *args, **kwargs):
    if created and not instance.folder_id:
        gdrive = gdriveAPI()
        if SystemValues.objects.count() and SystemValues.objects.all()[0].parent_folder:
            instance.folder_id = gdrive.create_folder(
                instance.name,
                SystemValues.objects.all()[0].parent_folder
            )
        else:
            instance.folder_id = gdrive.create_folder(instance.name)
        instance.save()

# @receiver(models.signals.m2m_changed, sender=Project.allowed_users.through)
@receiver(models.signals.post_save, sender=Project)
def prj_call_save2(sender, instance, *args, **kwargs):
    if instance.folder_id:
        folder_id = instance.folder_id
        gdrive = gdriveAPI()
        already_allowed = gdrive.get_permited_emails(folder_id)

        user_permissions=[]
        for user in instance.editor_users:
            if user and not user in already_allowed:
                user_permission = {
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress' : user
                }
                user_permissions.append(user_permission)
        gdrive.give_permissions(folder_id, user_permissions)

class ProjectObject(models.Model):
    name = models.CharField(
        max_length=120,
        default='',
        verbose_name='Название объекта'
    )
    folder_id = models.CharField(
        max_length=50,
        blank=True,
        unique=True,
        db_index=True,
        verbose_name='ID папки',
    )
    project = models.ForeignKey(
        'Project',
        on_delete=models.CASCADE,
        verbose_name='Проект'
    )
    main_file = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        unique=True,
        db_index=True,
        verbose_name='Основная таблица'
    )
    files_structure = JSONField(default={
        'graphs' : [],
        'documents' : [],
        'information' : [],
    }, blank=True)
    sync_task_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        unique=True,
        verbose_name='ID задачи синхронизации'
    )
    synced = models.BooleanField(
        default=False,
        verbose_name='Синхронизировано'
    )
    photo_folder_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        unique=True,
        verbose_name='ID папки с фотографиями',
    )
    photo_files_structure = JSONField(
        default={},
        blank=True,
        verbose_name='Структура файлов с фото'
    )

    history = HistoricalRecords()

    def get_synceing(self):
        return self.sync_task_id!=None

    def __str__(self):
        return self.name + ' ' + self.project.name

@receiver(models.signals.post_save, sender=ProjectObject)
def prj_obj_call_save(sender, instance, created, *args, **kwargs):
    if created:
        gdrive = gdriveAPI()
        if not instance.folder_id and instance.project.folder_id:
            instance.folder_id = gdrive.create_folder(
                instance.name,
                instance.project.folder_id
            )
        if not instance.photo_folder_id and instance.folder_id:
            instance.photo_folder_id = gdrive.create_folder(
                photo_folder_name,
                instance.folder_id
            )
            gdrive.give_permissions(instance.photo_folder_id, [{
                'type': 'anyone',
                'role': 'reader',
            }])
        instance.save()

class SystemValues(models.Model):
    changes_token = models.CharField(
        max_length=20,
        default='',
        unique=True,
        db_index=True,
        blank=True,
        verbose_name='Changes Token'
    )

    hidden_folder = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        unique=True,
        db_index=True,
        verbose_name='Скрытая папка'
    )

    parent_folder = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        unique=True,
        db_index=True,
        verbose_name='Основная папка для проектов'
    )

    def save(self, *args, **kwargs):
        if SystemValues.objects.exists() and not self.pk:
        # if you'll not check for self.pk
        # then error will also raised in update of exists model
            raise ValidationError('There is can be only one SystemValues instance')
        return super(SystemValues, self).save(*args, **kwargs)

@receiver(models.signals.post_save, sender=SystemValues)
def sys_vals_call_save(sender, instance, created, *args, **kwargs):
    if created:
        gdrive = gdriveAPI()
        if not instance.parent_folder:
            instance.parent_folder = gdrive.create_folder(root_folder_name)
        if not instance.hidden_folder:
            instance.hidden_folder = gdrive.create_folder(hidden_folder_name)

        instance.changes_token = gdrive.get_start_changes_token()
        instance.save()

def get_default_user():
    return User.objects.get(id=1)

class Contact(models.Model):
    name = models.CharField(
        max_length=120,
        default='',
        verbose_name='ФИО'
    )
    company = models.CharField(
        max_length=120,
        default='',
        verbose_name='Компания'
    )
    position = models.CharField(
        max_length=120,
        default='',
        verbose_name='Должность'
    )
    phone = models.CharField(
        max_length=120,
        default='',
        verbose_name='Телефон'
    )
    email = models.CharField(
        max_length=120,
        default='',
        blank=True,
        verbose_name='Email'
    )
    projects = models.ManyToManyField(
        Project,
        verbose_name='Проекты',
        blank=True
    )
    document_link = models.CharField(
        max_length=300,
        default='',
        verbose_name='Ссылка на утверждающий документ',
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Добавил контакт',
        default=None,
    )


    history = HistoricalRecords()

    def __str__(self):
        return self.name

class VideoFrame(models.Model):
    name = models.CharField(
        max_length=120,
        default='',
        verbose_name='Название трансляции'
    )
    iframe = models.TextField(
        default='',
        verbose_name='Код для вставки',
    )
    prj_object = models.ForeignKey(
        'ProjectObject',
        on_delete=models.CASCADE,
        verbose_name='Проект',
    )
