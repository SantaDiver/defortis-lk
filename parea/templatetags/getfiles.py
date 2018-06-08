from django import template
register = template.Library()

@register.filter
def getfiles(files_structure, file_type):
    return sorted(files_structure[file_type], key=lambda f: f['timestamp'])
