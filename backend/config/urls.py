from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# Auth imports
from incidents.auth import (
    login_view,
    logout_view,
    profile,
    register_user,
    CustomTokenObtainPairView
)

# Incidents imports
from incidents.views import (
    IncidentListCreateView,
    IncidentDetailView,
    DashboardStatsView,
    ClassifyIncidentView,
)

urlpatterns = [
    # 📁 Admin
    path('admin/', admin.site.urls),
    
    # 🔐 AUTENTICACIÓN
    path('api/auth/login/', login_view, name='login'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/profile/', profile, name='profile'),
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # 🚨 INCIDENTES
    path('api/incidents/', IncidentListCreateView.as_view(), name='incident-list-create'),
    path('api/incidents/<int:pk>/', IncidentDetailView.as_view(), name='incident-detail'),
    path('api/incidents/classify/', ClassifyIncidentView.as_view(), name='classify-incident'),
    
    # 📈 DASHBOARD
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
]
