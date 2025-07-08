from django.conf import settings

def version_static(request):
    return {
        'version': settings.VERSION_STATIC
    }