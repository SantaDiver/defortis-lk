from django import template
from django.contrib.auth.models import User
register = template.Library()

@register.filter
def firstname(id):
    try:
        user = User.objects.get(id=id)
        firstname = user.first_name
        lastname = user.last_name
        name = firstname + ' ' + lastname
        if name:
            return name
        else:
            return 'id %s' % id
    except  User.DoesNotExist:
        return 'Пользователь не найден'
