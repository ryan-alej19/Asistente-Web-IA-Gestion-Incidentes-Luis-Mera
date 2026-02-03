from django.urls import path
from . import views

urlpatterns = [
    path('analyze-file-preview/', views.analyze_file_preview),
    path('analyze-url-preview/', views.analyze_url_preview),
    path('create/', views.create_incident),
    path('list/', views.list_incidents),
    path('<int:incident_id>/', views.incident_detail),
]
