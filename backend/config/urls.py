"""
🔐 URLS PRINCIPALES DEL BACKEND - TESIS CIBERSEGURIDAD
Ryan Gallegos Mera - PUCEI
Última actualización: 30 de Diciembre, 2025
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# 🔐 Auth imports
from incidents.auth import (
    login_view,
    logout_view,
    profile,
    register_user,
    CustomTokenObtainPairView
)

# 🚨 Incidents imports
from incidents.views import (
    IncidentListCreateView,
    IncidentDetailView,
    DashboardStatsView,
    get_dashboard_stats,
    get_my_incidents,  
)

urlpatterns = [
    # ========================================
    # 📁 ADMIN PANEL
    # ========================================
    path('admin/', admin.site.urls),
    
    # ========================================
    # 🔐 AUTENTICACIÓN (JWT + Session)
    # ========================================
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/profile/', profile, name='profile'),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ========================================
    # 🚨 INCIDENTES CRUD
    # ========================================
    path('api/incidents/', IncidentListCreateView.as_view(), name='incident-list-create'),
path('api/incidents/<int:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
path('api/incidents/my-incidents/', get_my_incidents, name='my-incidents'),  # ← NUEVA
path('api/incidents/dashboard-stats/', get_dashboard_stats, name='dashboard-stats'), 
    
    # ========================================
    # 🤖 IA CLASIFICADOR (Testing)
    # ========================================
    
    
    # ========================================
    # 📈 DASHBOARD STATS
    # ========================================
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
