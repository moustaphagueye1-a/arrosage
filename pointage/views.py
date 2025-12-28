# pointage/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import GroupeArrosage, Arrosage
from .utils import verifier_position_champ


def verifier_gps_view(request):
    """
    Vue pour vérifier la position GPS avant d'afficher le formulaire
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
            
            dans_rayon, distance = verifier_position_champ(latitude, longitude)
            
            if dans_rayon:
                # Stocker les coordonnées en session
                request.session['latitude'] = latitude
                request.session['longitude'] = longitude
                return JsonResponse({
                    'success': True,
                    'message': f'Position validée ! Distance : {distance}m',
                    'redirect_url': '/pointage/formulaire/'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Vous êtes trop éloigné du champ ! Distance : {distance}m (maximum {settings.CHAMP_RAYON_METRES}m)',
                    'distance': distance
                })
        
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur : {str(e)}'
            })
    
    # Afficher la page de vérification GPS
    return render(request, 'pointage/verifier_gps.html')


@login_required
def formulaire_arrosage_view(request):
    """
    Formulaire principal de pointage
    """
    # Vérifier qu'on a les coordonnées GPS en session
    if 'latitude' not in request.session or 'longitude' not in request.session:
        messages.error(request, "Veuillez d'abord autoriser la géolocalisation.")
        return redirect('verifier_gps')
    
    # Vérifier si l'utilisateur a déjà un arrosage en cours
    arrosage_en_cours = Arrosage.objects.filter(
        utilisateur=request.user,
        statut='en_cours'
    ).first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'demarrer':
            # Vérifier à nouveau qu'il n'y a pas d'arrosage en cours
            if arrosage_en_cours:
                messages.warning(request, "Vous avez déjà un arrosage en cours !")
                return redirect('formulaire_arrosage')
            
            groupe_id = request.POST.get('groupe')
            groupe = get_object_or_404(GroupeArrosage, id=groupe_id)
            
            # Créer un nouvel arrosage
            arrosage = Arrosage.objects.create(
                utilisateur=request.user,
                groupe=groupe,
                heure_debut=timezone.now(),
                latitude_debut=request.session['latitude'],
                longitude_debut=request.session['longitude'],
                statut='en_cours'
            )
            
            messages.success(request, f"Arrosage démarré pour {groupe.nom} à {arrosage.heure_debut.strftime('%H:%M')}")
            return redirect('formulaire_arrosage')
        
        elif action == 'terminer':
            if not arrosage_en_cours:
                messages.error(request, "Aucun arrosage en cours à terminer !")
                return redirect('formulaire_arrosage')
            
            # Vérifier à nouveau la position GPS
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            
            dans_rayon, distance = verifier_position_champ(latitude, longitude)
            
            if not dans_rayon:
                messages.error(request, f"Vous devez être au champ pour terminer l'arrosage ! Distance : {distance}m")
                return redirect('formulaire_arrosage')
            
            # Terminer l'arrosage
            arrosage_en_cours.heure_fin = timezone.now()
            arrosage_en_cours.latitude_fin = latitude
            arrosage_en_cours.longitude_fin = longitude
            arrosage_en_cours.calculer_duree()
            arrosage_en_cours.valider_arrosage()
            
            if arrosage_en_cours.statut == 'valide':
                messages.success(request, f"Arrosage terminé et validé ! Durée : {arrosage_en_cours.duree_minutes} minutes")
            else:
                messages.warning(request, f"Arrosage terminé mais invalide : {arrosage_en_cours.commentaire}")
            
            # Nettoyer la session
            del request.session['latitude']
            del request.session['longitude']
            
            return redirect('historique_arrosages')
    
    # Afficher le formulaire
    groupes = GroupeArrosage.objects.all()
    
    context = {
        'groupes': groupes,
        'arrosage_en_cours': arrosage_en_cours,
    }
    
    return render(request, 'pointage/formulaire_arrosage.html', context)


@login_required
def historique_arrosages_view(request):
    """
    Affiche l'historique des arrosages de l'utilisateur
    """
    arrosages = Arrosage.objects.filter(utilisateur=request.user)
    
    context = {
        'arrosages': arrosages,
    }
    
    return render(request, 'pointage/historique.html', context)


@login_required
def tableau_bord_view(request):
    """
    Tableau de bord administrateur (statistiques)
    """
    if not request.user.is_staff:
        messages.error(request, "Accès réservé aux administrateurs")
        return redirect('formulaire_arrosage')
    
    arrosages = Arrosage.objects.all()
    groupes = GroupeArrosage.objects.all()
    
    # Statistiques
    total_arrosages = arrosages.count()
    arrosages_valides = arrosages.filter(statut='valide').count()
    arrosages_invalides = arrosages.filter(statut='invalide').count()
    arrosages_en_cours = arrosages.filter(statut='en_cours').count()
    
    context = {
        'arrosages': arrosages[:50],  # Limiter à 50 pour l'affichage
        'groupes': groupes,
        'total_arrosages': total_arrosages,
        'arrosages_valides': arrosages_valides,
        'arrosages_invalides': arrosages_invalides,
        'arrosages_en_cours': arrosages_en_cours,
    }
    
    return render(request, 'pointage/tableau_bord.html', context)