from django.db import models
from django.contrib.auth.models import User

class Incident(models.Model):
    """
    Modelo para almacenar incidentes de seguridad reportados.
    Cada incidente puede ser una URL o un archivo sospechoso.
    """
    
    RISK_LEVELS = [
        ('LOW', 'Bajo'),
        ('MEDIUM', 'Medio'),
        ('HIGH', 'Alto'),
        ('CRITICAL', 'Critico'),
        ('UNKNOWN', 'Desconocido'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('investigating', 'En Investigacion'),
        ('resolved', 'Resuelto'),
    ]
    
    TYPE_CHOICES = [
        ('url', 'URL'),
        ('file', 'Archivo'),
    ]
    
    # Campos basicos
    incident_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)
    attached_file = models.FileField(upload_to='incidents/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    
    # Resultados de analisis
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='UNKNOWN')
    virustotal_result = models.JSONField(blank=True, null=True)
    phishtank_result = models.JSONField(blank=True, null=True)
    metadefender_result = models.JSONField(blank=True, null=True)
    gemini_analysis = models.TextField(blank=True, default='')
    
    # Metadatos
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
    
    def __str__(self):
        return f"Incidente #{self.id} - {self.get_risk_level_display()}"
