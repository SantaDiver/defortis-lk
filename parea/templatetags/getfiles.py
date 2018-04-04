from django import template
register = template.Library()

@register.filter
def getfiles(files_structure, file_type):
    return files_structure[file_type]
