from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pointage import views as pointage_views  # <-- importer tes vues

urlpatterns = [
    path('admin/', admin.site.urls),
    path('pointage/', include('pointage.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # Pour login/logout

    # Ajouter la racine pour afficher la page de vérification GPS
    path('', pointage_views.verifier_gps_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
