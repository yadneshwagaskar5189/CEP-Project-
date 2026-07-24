from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Hospital, Specialisation


def _filtered(request):
    qs = (
        Hospital.objects.filter(is_active=True)
        .prefetch_related("specialisations", "bed_records")
    )

    city = request.GET.get("city", "")
    query = request.GET.get("q", "").strip()
    spec = request.GET.get("spec", "")
    htype = request.GET.get("type", "")
    only_pmjay = request.GET.get("pmjay") == "1"

    if city:
        qs = qs.filter(city__iexact=city)
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(area__icontains=query) | Q(address__icontains=query)
        )
    if spec:
        qs = qs.filter(specialisations__name=spec)
    if htype:
        qs = qs.filter(hospital_type=htype)
    if only_pmjay:
        qs = qs.filter(accepts_pmjay=True)

    hospitals = list(qs.distinct())

    # Largest hospitals first. This used to sort by free beds, which is no
    # longer shown - capacity is the nearest equivalent ordering that still
    # matches something displayed on the card.
    hospitals.sort(key=lambda h: (h.beds.total_beds if h.beds else -1), reverse=True)
    return hospitals, {
        "city": city, "query": query, "spec": spec,
        "type": htype, "pmjay": only_pmjay,
    }


def hospital_list(request):
    hospitals, active = _filtered(request)

    cities = (
        Hospital.objects.filter(is_active=True)
        .values_list("city", flat=True).distinct().order_by("city")
    )

    total_capacity = sum(h.beds.total_beds for h in hospitals if h.beds)

    # The district list runs past a hundred entries, and each card carries a
    # bed panel, so the page is paginated. The capacity total above is for the
    # whole filtered set, not just this page.
    paginator = Paginator(hospitals, 20)
    page = paginator.get_page(request.GET.get("page"))

    # Every filter except `page`, so the pager links keep the current filters.
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "hospitals": page.object_list,
        "page_obj": page,
        "paginator": paginator,
        "querystring": querystring,
        "cities": cities,
        "specialisations": Specialisation.objects.all(),
        "types": Hospital.TYPE_CHOICES,
        "active": active,
        "result_count": len(hospitals),
        "total_capacity": total_capacity,
    }
    return render(request, "hospitals/list.html", context)


def hospital_detail(request, pk):
    hospital = get_object_or_404(
        Hospital.objects.prefetch_related("specialisations", "bed_records"),
        pk=pk, is_active=True,
    )
    nearby = Hospital.objects.filter(
        is_active=True, city=hospital.city
    ).exclude(pk=hospital.pk).prefetch_related("bed_records")[:4]
    return render(request, "hospitals/detail.html", {"hospital": hospital, "nearby": nearby})


def beds_api(request):
    """Small JSON endpoint so the bed counts can refresh without a page reload."""
    hospitals, _ = _filtered(request)
    payload = []
    for h in hospitals:
        record = h.beds
        if not record:
            continue
        payload.append({
            "id": h.id,
            "name": h.name,
            "free": record.total_free,
            "total": record.total_beds,
            "status": record.status,
            "general": record.general_available,
            "icu": record.icu_available,
            "oxygen": record.oxygen_available,
            "ventilator": record.ventilator_available,
            "updated": record.last_updated.isoformat(),
        })
    return JsonResponse({"hospitals": payload, "count": len(payload)})
