from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """
    Administrador de Incidentes.
    Interfaz simplificada para el nuevo modelo de Incident.
    """
    
    list_display = [
        'id',
        'incident_type',
        'risk_level_badge',
        'status',
        'created_at',
        'reported_by'
    ]
    
    list_filter = [
        'risk_level',
        'status',
        'incident_type',
        'created_at',
        'reported_by',
    ]
    
    search_fields = [
        'description',
        'url',
        'gemini_analysis',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'virustotal_result',
        'phishtank_result',
        'metadefender_result',
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('incident_type', 'url', 'attached_file', 'description')
        }),
        ('Estado y Riesgo', {
            'fields': ('risk_level', 'status', 'reported_by')
        }),
        ('Resultados de Análisis', {
            'fields': ('gemini_analysis', 'virustotal_result', 'phishtank_result', 'metadefender_result'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def risk_level_badge(self, obj):
        """Muestra el nivel de riesgo con color"""
        colors = {
            'LOW': 'background-color: #28a745; color: white;',
            'MEDIUM': 'background-color: #ffc107; color: black;',
            'HIGH': 'background-color: #fd7e14; color: white;',
            'CRITICAL': 'background-color: #dc3545; color: white;',
            'UNKNOWN': 'background-color: #6c757d; color: white;',
        }
        style = colors.get(obj.risk_level, 'background-color: #6c757d; color: white;')
        return f'<span style="{style} padding: 5px 10px; border-radius: 3px; font-weight: bold;">{obj.get_risk_level_display()}</span>'
    
    risk_level_badge.short_description = 'Nivel de Riesgo'
    risk_level_badge.allow_tags = True
