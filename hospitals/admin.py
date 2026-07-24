from django.contrib import admin
from django.utils.html import format_html

from .models import BedAvailability, Hospital, Specialisation


class BedInline(admin.StackedInline):
    model = BedAvailability
    extra = 0
    max_num = 1
    fields = (
        "total_beds",
        ("general_available", "icu_available"),
        ("oxygen_available", "ventilator_available"),
        "updated_by",
    )


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "hospital_type", "beds_summary", "accepts_pmjay", "is_active")
    list_filter = ("city", "hospital_type", "accepts_pmjay", "has_emergency", "is_active")
    search_fields = ("name", "area", "city", "pincode")
    filter_horizontal = ("specialisations",)
    inlines = [BedInline]
    fieldsets = (
        ("Identity", {"fields": ("name", "hospital_type", "is_active")}),
        ("Where it is", {"fields": ("address", "area", "city", "district", "pincode",
                                    ("latitude", "longitude"))}),
        ("Contact", {"fields": ("contact_number", "emergency_number")}),
        ("Services", {"fields": ("specialisations", "has_emergency", "has_ambulance",
                                 "accepts_pmjay")}),
    )

    @admin.display(description="Free beds")
    def beds_summary(self, obj):
        record = obj.beds
        if not record:
            return format_html('<span style="color:#999">no data</span>')
        colour = {"open": "#0E7A57", "limited": "#C8791B", "full": "#B03A2E"}[record.status]
        return format_html(
            '<b style="color:{}">{} free</b> <span style="color:#777">of {}</span>',
            colour, record.total_free, record.total_beds,
        )


@admin.register(BedAvailability)
class BedAvailabilityAdmin(admin.ModelAdmin):
    """
    This is the screen hospital staff use. It is deliberately editable straight
    from the list view so updating a whole city takes one page and one Save.
    """

    list_display = ("hospital", "total_beds", "general_available", "icu_available",
                    "oxygen_available", "ventilator_available", "free_display",
                    "freshness", "last_updated")
    list_editable = ("total_beds", "general_available", "icu_available",
                     "oxygen_available", "ventilator_available")
    list_filter = ("hospital__city", "hospital__hospital_type")
    search_fields = ("hospital__name", "hospital__city")
    list_select_related = ("hospital",)
    readonly_fields = ("last_updated",)

    @admin.display(description="Status")
    def free_display(self, obj):
        colour = {"open": "#0E7A57", "limited": "#C8791B", "full": "#B03A2E"}[obj.status]
        return format_html(
            '<b style="color:{}">{}</b> ({}% free)', colour, obj.status_label, obj.free_percent
        )

    @admin.display(description="Fresh?")
    def freshness(self, obj):
        if obj.is_stale:
            return format_html('<span style="color:#B03A2E">needs update</span>')
        return format_html('<span style="color:#0E7A57">up to date</span>')


admin.site.register(Specialisation)
