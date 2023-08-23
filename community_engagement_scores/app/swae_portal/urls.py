from django.urls import path

from . import views


app_name = "swae_portal"

urlpatterns = [
    path("", views.DataAnalysis.as_view(), name="data_analysis"),
    path(
        "download/<str:filename>/", views.FileDownloader.as_view(), name="download_file"
    ),
]
