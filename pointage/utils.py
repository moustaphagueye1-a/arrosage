# pointage/utils.py

import math
from django.conf import settings

def calculer_distance_haversine(lat1, lon1, lat2, lon2):
    """
    Calcule la distance en mètres entre deux coordonnées GPS
    Formule de Haversine
    """
    # Rayon de la Terre en mètres
    R = 6371000
    
    # Conversion en radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Formule de Haversine
    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * \
        math.sin(delta_lon / 2) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return distance


def verifier_position_champ(latitude, longitude):
    """
    Vérifie si l'utilisateur est dans le rayon autorisé du champ
    Retourne (bool, distance_en_metres)
    """
    distance = calculer_distance_haversine(
        settings.CHAMP_LATITUDE,
        settings.CHAMP_LONGITUDE,
        latitude,
        longitude
    )
    
    dans_rayon = distance <= settings.CHAMP_RAYON_METRES
    
    return dans_rayon, round(distance, 2)