from django.urls import path
from . import views

urlpatterns = [
    path('analyze-file-preview/', views.analyze_file_preview, name='analyze_file_preview'),
    path('analyze-url-preview/', views.analyze_url_preview, name='analyze_url_preview'),
    path('analyze-image-preview/', views.analyze_image_preview, name='analyze_image_preview'),
    path('create/', views.create_incident, name='create_incident'),
    path('list/', views.list_incidents, name='list_incidents'),
    path('<int:incident_id>/', views.incident_detail, name='incident_detail'),
    path('stats/', views.incident_stats, name='incident_stats'),
    path('<int:incident_id>/update-status/', views.update_incident_status, name='update_incident_status'),
    path('<int:incident_id>/notes/', views.manage_incident_notes, name='manage_incident_notes'),
    path('<int:incident_id>/analysis-details/', views.get_incident_analysis_details, name='get_incident_analysis_details'),
    path('<int:incident_id>/pdf/', views.generate_pdf_report, name='generate_pdf_report'),
    path('export/csv/', views.export_incidents_csv, name='export_incidents_csv'),
    path('report/pdf/monthly/', views.generate_pdf_report, name='pdf_monthly'),
    path('report/pdf/<int:incident_id>/', views.generate_pdf_report, name='pdf_incident'),
]
