from django.conf import settings


def site_info(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_TAGLINE": settings.SITE_TAGLINE,
        "EMERGENCY_NUMBER": settings.EMERGENCY_NUMBER,
    }
