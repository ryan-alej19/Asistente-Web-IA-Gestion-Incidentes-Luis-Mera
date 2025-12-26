from django.contrib import admin
from .models import Incident

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    """
    Administrador de Incidentes
    Interfaz para gestionar incidentes detectados
    """
    
    list_display = [
        'title',
        'severity_badge',
        'status',
        'confidence_percentage',
        'detected_at',
        'assigned_to'
    ]
    
    list_filter = [
        'severity',
        'status',
        'threat_type',
        'detected_at',
    ]
    
    search_fields = [
        'title',
        'description',
        'threat_type',
        'ip_source',
        'ip_destination',
    ]
    
    readonly_fields = [
        'detected_at',
        'created_at',
        'updated_at',
        'confidence_percentage',
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description')
        }),
        ('Seguridad y Clasificación', {
            'fields': ('severity', 'status', 'threat_type')
        }),
        ('Detección por IA', {
            'fields': ('confidence', 'confidence_percentage'),
            'description': 'Valores de confianza de la detección automática'
        }),
        ('Red e IPs', {
            'fields': ('ip_source', 'ip_destination', 'log_source')
        }),
        ('Asignación y Notas', {
            'fields': ('assigned_to', 'notes')
        }),
        ('Auditoría (Solo Lectura)', {
            'fields': ('detected_at', 'created_at', 'updated_at', 'resolved_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_false_positive', 'mark_as_critical']
    
    def severity_badge(self, obj):
        """Muestra la severidad con color"""
        colors = {
            'low': 'background-color: #28a745; color: white;',
            'medium': 'background-color: #ffc107; color: black;',
            'high': 'background-color: #fd7e14; color: white;',
            'critical': 'background-color: #dc3545; color: white;',
        }
        style = colors.get(obj.severity, 'background-color: #6c757d;')
        return f'<span style="{style} padding: 5px 10px; border-radius: 3px; font-weight: bold;">{obj.get_severity_display()}</span>'
    
    severity_badge.short_description = 'Severidad'
    severity_badge.allow_tags = True
    
    def confidence_percentage(self, obj):
        """Muestra confianza como porcentaje"""
        percentage = int(obj.confidence * 100)
        color = 'green' if percentage > 80 else 'orange' if percentage > 50 else 'red'
        return f'<span style="color: {color}; font-weight: bold;">{percentage}%</span>'
    
    confidence_percentage.short_description = 'Confianza (%)'
    confidence_percentage.allow_tags = True
    
    def mark_as_resolved(self, request, queryset):
        """Acción para marcar como resuelto"""
        from django.utils import timezone
        updated = queryset.update(status='resolved', resolved_at=timezone.now())
        self.message_user(request, f'{updated} incidentes marcados como resueltos.')
    
    mark_as_resolved.short_description = '✅ Marcar como Resuelto'
    
    def mark_as_false_positive(self, request, queryset):
        """Acción para marcar como falsa alarma"""
        updated = queryset.update(status='false_positive')
        self.message_user(request, f'{updated} incidentes marcados como falsas alarmas.')
    
    mark_as_false_positive.short_description = '❌ Marcar como Falsa Alarma'
    
    def mark_as_critical(self, request, queryset):
        """Acción para marcar como crítico"""
        updated = queryset.update(severity='critical', status='under_review')
        self.message_user(request, f'{updated} incidentes marcados como críticos.')
    
    mark_as_critical.short_description = '🚨 Marcar como Crítico'
    
    class Media:
        css = {
            'all': ['admin/css/admin_custom.css']
        }
