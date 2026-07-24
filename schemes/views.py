from django.shortcuts import get_object_or_404, render

from .models import Scheme


def scheme_list(request):
    qs = Scheme.objects.filter(is_active=True)

    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    level = request.GET.get("level", "")
    card = request.GET.get("card", "")

    if query:
        from django.db.models import Q
        qs = qs.filter(
            Q(name__icontains=query)
            | Q(short_name__icontains=query)
            | Q(headline_benefit__icontains=query)
            | Q(description__icontains=query)
            | Q(eligibility__icontains=query)
        )
    if category:
        qs = qs.filter(category=category)
    if level:
        qs = qs.filter(level=level)
    if card:
        # "any" schemes are open to everyone, so always include them.
        from django.db.models import Q
        qs = qs.filter(Q(eligible_cards=card) | Q(eligible_cards="any"))

    context = {
        "schemes": qs,
        "query": query,
        "active_category": category,
        "active_level": level,
        "active_card": card,
        "categories": Scheme.CATEGORY_CHOICES,
        "cards": Scheme.CARD_CHOICES,
        "total": Scheme.objects.filter(is_active=True).count(),
    }
    return render(request, "schemes/list.html", context)


def scheme_detail(request, slug):
    scheme = get_object_or_404(Scheme, slug=slug, is_active=True)
    related = Scheme.objects.filter(
        is_active=True, category=scheme.category
    ).exclude(pk=scheme.pk)[:3]
    return render(request, "schemes/detail.html", {"scheme": scheme, "related": related})
