"""
🛡️ URL Configuration - TESIS CIBERSEGURIDAD
Ryan Gallegos Mera - PUCESI
Última actualización: 04 de Enero, 2026
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # ========================================
    # 🔐 AUTENTICACIÓN JWT
    # ========================================
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ========================================
    # 📋 GESTIÓN DE INCIDENTES
    # ========================================
    path('api/incidents/', include('incidents.urls')),
    
    # ========================================
    # 🛠️ ADMIN PANEL
    # ========================================
    path('admin/', admin.site.urls),
]
