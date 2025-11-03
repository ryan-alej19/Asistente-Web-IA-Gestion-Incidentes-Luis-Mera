from django.contrib import admin
from django.urls import path
from incidents import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/incidents/', views.get_incidents, name='get_incidents'),
    path('api/incidents/analyze/', views.analyze_incident, name='analyze_incident'),
    path('api/dashboard/stats/', views.get_dashboard_stats, name='dashboard_stats'),
    path('api/incidents/update-status/', views.update_incident_status, name='update_incident_status'),
]
