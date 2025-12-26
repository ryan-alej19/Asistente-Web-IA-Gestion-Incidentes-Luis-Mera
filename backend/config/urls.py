from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
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
]
