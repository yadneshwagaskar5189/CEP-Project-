from django.db.models import Count
from django.shortcuts import render

from hospitals.models import BedAvailability, Hospital
from prediction.engine import model_metadata, model_is_ready
from schemes.models import Scheme

from .models import HealthTip


def home(request):
    beds = BedAvailability.objects.select_related("hospital")
    total_capacity = sum(b.total_beds for b in beds)

    context = {
        "featured_schemes": Scheme.objects.filter(is_active=True)[:3],
        "tips": HealthTip.objects.filter(is_active=True)[:6],
        "stat_schemes": Scheme.objects.filter(is_active=True).count(),
        "stat_hospitals": Hospital.objects.filter(is_active=True).count(),
        "stat_bed_capacity": total_capacity,
        "stat_cities": Hospital.objects.filter(is_active=True)
                        .values("city").distinct().count(),
    }
    return render(request, "core/home.html", context)


def about(request):
    context = {
        "meta": model_metadata() if model_is_ready() else None,
        "scheme_by_level": Scheme.objects.filter(is_active=True)
                             .values("level").annotate(n=Count("id")),
    }
    return render(request, "core/about.html", context)
