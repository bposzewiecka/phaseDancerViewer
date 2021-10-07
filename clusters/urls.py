from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('clusters', views.clusters, name='clusters'),
    path('assembly/<int:p_id>/<int:p_number>', views.assembly, name='assembly'),
    path('igv', views.igv, name='igv'),

]


