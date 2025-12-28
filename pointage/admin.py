# pointage/admin.py

from django.contrib import admin
from .models import GroupeArrosage, Arrosage

@admin.register(GroupeArrosage)
class GroupeArrosageAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description', 'date_creation']
    search_fields = ['nom', 'description']
    list_filter = ['date_creation']

@admin.register(Arrosage)
class ArrosageAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'groupe', 'heure_debut', 'heure_fin', 'duree_minutes', 'statut']
    list_filter = ['statut', 'groupe', 'heure_debut']
    search_fields = ['utilisateur__username', 'groupe__nom']
    readonly_fields = ['duree_minutes', 'date_creation', 'date_modification']
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('utilisateur', 'groupe', 'statut')
        }),
        ('Horodatage', {
            'fields': ('heure_debut', 'heure_fin', 'duree_minutes')
        }),
        ('Géolocalisation', {
            'fields': ('latitude_debut', 'longitude_debut', 'latitude_fin', 'longitude_fin')
        }),
        ('Autres', {
            'fields': ('commentaire', 'date_creation', 'date_modification')
        }),
    )