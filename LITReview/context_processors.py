from django.conf import settings

# Context processor : ajoute la variable 'version' pour la gestion du cache des fichiers statiques
# injecter une variable dans tous les templates, pour forcer le rafraîchissement du cache navigateur.


def version_static(request):
    """
    Context processors for the LITReview Django app.

    These functions inject additional context variables into templates for all views
    when configured in the project's TEMPLATES setting.

    Available context processors:
    - version_static: Adds a 'version' variable from settings.VERSION_STATIC,
    allowing cache busting for static files in templates.

    Usage:
    - Add 'LITReview.context_processors.version_static' to the 'context_processors' list
    in your TEMPLATES setting in settings.py to make the 'version' variable available
    in all templates.
    """
    return {
        'version': settings.VERSION_STATIC
    }
