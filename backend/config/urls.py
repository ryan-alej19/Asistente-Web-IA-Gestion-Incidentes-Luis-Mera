from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from incidents.views import IncidentViewSet, create_incident_report_from_form

# Router para las vistas automáticas
router = DefaultRouter()
router.register(r'incidents', IncidentViewSet, basename='incident')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/create-report/', create_incident_report_from_form, name='create-report'),
]
