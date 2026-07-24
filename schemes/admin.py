from django.contrib import admin

from .models import Scheme


@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "level", "category", "eligible_cards",
                    "last_verified", "is_active")
    list_filter = ("level", "category", "eligible_cards", "is_active")
    search_fields = ("name", "short_name", "headline_benefit", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active",)
    fieldsets = (
        ("Identity", {"fields": ("name", "short_name", "slug", "level", "category",
                                 "display_order", "is_active")}),
        ("What the citizen gets", {"fields": ("headline_benefit", "description")}),
        ("Who qualifies", {"fields": ("eligible_cards", "eligibility")}),
        ("How to apply", {"fields": ("documents", "application_steps", "where_to_apply")}),
        ("Official source", {"fields": ("official_link", "helpline", "last_verified"),
                             "description": "Always re-check the official portal before "
                                            "changing benefit amounts, then update the "
                                            "verification date."}),
    )
