# pointage/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class GroupeArrosage(models.Model):
    """Représente un groupe/zone d'arrosage dans le champ"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Groupe d'arrosage"
        verbose_name_plural = "Groupes d'arrosage"
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class Arrosage(models.Model):
    """Enregistre un pointage d'arrosage"""
    
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('invalide', 'Invalidé'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arrosages')
    groupe = models.ForeignKey(GroupeArrosage, on_delete=models.CASCADE, related_name='arrosages')
    
    # Horodatage
    heure_debut = models.DateTimeField()
    heure_fin = models.DateTimeField(null=True, blank=True)
    duree_minutes = models.IntegerField(null=True, blank=True)
    
    # GPS
    latitude_debut = models.FloatField()
    longitude_debut = models.FloatField()
    latitude_fin = models.FloatField(null=True, blank=True)
    longitude_fin = models.FloatField(null=True, blank=True)
    
    # Validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    commentaire = models.TextField(blank=True, null=True)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Arrosage"
        verbose_name_plural = "Arrosages"
        ordering = ['-heure_debut']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.groupe.nom} - {self.heure_debut.strftime('%d/%m/%Y %H:%M')}"
    
    def calculer_duree(self):
        """Calcule la durée en minutes"""
        if self.heure_fin and self.heure_debut:
            delta = self.heure_fin - self.heure_debut
            self.duree_minutes = int(delta.total_seconds() / 60)
            return self.duree_minutes
        return None
    
    def valider_arrosage(self):
        """Valide si durée >= 20 minutes"""
        if self.duree_minutes is not None:
            if self.duree_minutes >= 20:
                self.statut = 'valide'
            else:
                self.statut = 'invalide'
                self.commentaire = f"Durée insuffisante : {self.duree_minutes} minutes (minimum 20 minutes requis)"
            self.save()