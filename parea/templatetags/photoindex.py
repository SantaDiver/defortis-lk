from django import template
register = template.Library()

@register.filter
def photoindex(Dict, modifiedTime):
    return Dict[modifiedTime]
