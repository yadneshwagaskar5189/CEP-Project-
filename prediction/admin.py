from django.contrib import admin
from django.utils.html import format_html

from .models import DiseaseInfo, SymptomCheck


@admin.register(DiseaseInfo)
class DiseaseInfoAdmin(admin.ModelAdmin):
    list_display = ("name", "specialisation", "urgency", "has_warnings", "sensitive")
    list_filter = ("specialisation", "urgency", "sensitive")
    search_fields = ("name", "about", "precautions", "avoid")
    fieldsets = (
        ("Condition", {"fields": ("name", "specialisation", "urgency", "sensitive")}),
        ("What it is", {"fields": ("about",)}),
        ("What to do", {"fields": ("precautions", "tests")}),
        ("Drug safety", {
            "fields": ("avoid",),
            "description": "What NOT to take. This app never names a medicine to take - "
                           "dengue and flu are commonly confused and ibuprofen is "
                           "ordinary for one and dangerous for the other.",
        }),
    )

    @admin.display(description="Drug warnings", boolean=True)
    def has_warnings(self, obj):
        return bool(obj.avoid.strip())


@admin.register(SymptomCheck)
class SymptomCheckAdmin(admin.ModelAdmin):
    list_display = ("created_at", "predicted_disease", "urgency_badge", "confidence",
                    "red_flag", "symptom_count", "used_labs", "used_ocr",
                    "answered_questions", "city")
    list_filter = ("urgency", "predicted_disease", "red_flag", "used_labs", "used_ocr", "city")
    date_hierarchy = "created_at"
    readonly_fields = [f.name for f in SymptomCheck._meta.fields]

    def has_add_permission(self, request):
        return False

    @admin.display(description="Urgency")
    def urgency_badge(self, obj):
        colours = {"routine": "#2C6E63", "prompt": "#A8760A",
                   "urgent": "#C2560F", "emergency": "#B3261E"}
        c = colours.get(obj.urgency, "#777")
        return format_html('<b style="color:{}">{}</b>', c, obj.urgency or "-")
