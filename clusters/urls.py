from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contig/<int:p_id>/<int:p_number>/<p_type>", views.contig, name="contig"),
    path("igv", views.igv, name="igv"),
]
