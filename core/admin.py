from django.contrib import admin

from .models import HealthTip


@admin.register(HealthTip)
class HealthTipAdmin(admin.ModelAdmin):
    list_display = ("title", "icon", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
