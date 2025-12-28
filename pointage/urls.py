# pointage/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.verifier_gps_view, name='verifier_gps'),
    path('formulaire/', views.formulaire_arrosage_view, name='formulaire_arrosage'),
    path('historique/', views.historique_arrosages_view, name='historique_arrosages'),
    path('tableau-bord/', views.tableau_bord_view, name='tableau_bord'),
]