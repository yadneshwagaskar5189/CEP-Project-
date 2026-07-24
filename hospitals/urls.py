from django.urls import path

from . import views

app_name = "hospitals"

urlpatterns = [
    path("", views.hospital_list, name="list"),
    path("api/beds/", views.beds_api, name="beds_api"),
    path("<int:pk>/", views.hospital_detail, name="detail"),
]
