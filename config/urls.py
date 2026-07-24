from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Arogya Setu Kendra - Control Panel"
admin.site.site_title = "Arogya Setu Kendra"
admin.site.index_title = "Manage schemes, hospitals and bed availability"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("schemes/", include("schemes.urls")),
    path("hospitals/", include("hospitals.urls")),
    path("symptom-checker/", include("prediction.urls")),
]
