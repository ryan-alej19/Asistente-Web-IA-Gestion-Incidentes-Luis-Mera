from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from rest_framework_simplejwt.views import TokenRefreshView
from incidents.views import IncidentViewSet, create_incident_report_from_form
from incidents.auth import CustomTokenObtainPairView, register_user, profile


# Crear el router
router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')


urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints del ViewSet
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # JWT endpoints
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/profile/', profile, name='profile'),
    
    # NUEVO: Endpoint del formulario
    path('api/create-report/', create_incident_report_from_form, name='create_incident_report'),
=======
from incidents.views import IncidentViewSet

# Crear router para ViewSet
router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Todas las rutas del ViewSet se incluyen automáticamente
    # GET    /api/incidents/          - Listar todos
    # POST   /api/incidents/          - Crear nuevo
    # GET    /api/incidents/{id}/     - Detalle
    # PUT    /api/incidents/{id}/     - Actualizar
    # DELETE /api/incidents/{id}/     - Eliminar
    # POST   /api/incidents/{id}/analyze/ - Análisis IA
    # GET    /api/incidents/stats/    - Estadísticas
    path('api/', include(router.urls)),
>>>>>>> 0ac16d3a1f6351a133051af9b8c67e4f08d6cd60
]
