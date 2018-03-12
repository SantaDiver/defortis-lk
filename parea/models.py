from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.auth.models import User
from django.dispatch import receiver
import sys

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
        verbose_name='Допущенные пользователи',
        blank=True
    )
    history = HistoricalRecords()

    def __str__(self):
        return self.name

@receiver(models.signals.post_save, sender=Project)
def prj_call_save(sender, instance, created, *args, **kwargs):
    if created and not instance.folder_id:
        gdrive = gdriveAPI()
        instance.folder_id = gdrive.create_folder(instance.name)
        instance.save()
    # TODO: test below code
    if instance.folder_id:
        gdrive = gdriveAPI()
        user_permissions=[]
        for user in instance.allowed_users:
            user_permission = {
                'type': 'user',
                'role': 'writer',
                'emailAddress' : user.emailAddress
            }
            user_permissions.append(user_permission)
        gdrive.give_permissions(instance.folder_id, user_permissions)

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

    history = HistoricalRecords()

@receiver(models.signals.post_save, sender=ProjectObject)
def prj_obj_call_save(sender, instance, created, *args, **kwargs):
    if created and not instance.folder_id and instance.project.folder_id:
        gdrive = gdriveAPI()
        instance.folder_id = gdrive.create_folder(
            instance.name,
            instance.project.folder_id
        )
        instance.save()
