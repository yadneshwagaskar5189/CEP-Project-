from django.urls import path

from . import views

app_name = "prediction"

urlpatterns = [
    path("", views.start, name="start"),
    path("context/", views.context, name="context"),
    path("report/", views.labs, name="labs"),
    path("questions/", views.questions, name="questions"),
    path("result/", views.result, name="result"),
    path("reset/", views.reset, name="reset"),
]
