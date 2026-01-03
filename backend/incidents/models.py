from django.db import models
from django.contrib.auth.models import AbstractUser, User
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado con roles para la tesis
    Roles: admin (gestor del sistema), analyst (analista SOC), employee (reporta incidentes)
    """
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('analyst', 'Analista SOC'),
        ('employee', 'Empleado'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        help_text="Rol del usuario en el sistema"
    )
    
    class Meta:
        db_table = 'custom_users'
        verbose_name = 'Usuario Personalizado'
        verbose_name_plural = 'Usuarios Personalizados'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_analyst(self):
        return self.role == 'analyst'
    
    def is_employee(self):
        return self.role == 'employee'


class Incident(models.Model):
    """
    Modelo de Incidente de Seguridad
    Almacena reportes de incidentes detectados o reportados por usuarios
    """
    
    # Estados posibles del incidente
    STATUS_CHOICES = [
        ('new', 'Nuevo'),
        ('under_review', 'En Revisión'),
        ('resolved', 'Resuelto'),
        ('false_positive', 'Falsa Alarma'),
        ('in_progress', 'En Progreso'),
    ]
    
    # Niveles de severidad
    SEVERITY_CHOICES = [
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]
    
    # Campos principales
    title = models.CharField(max_length=255, help_text="Título del incidente")
    description = models.TextField(help_text="Descripción detallada del incidente")
    
    # 🔥 NUEVO: Campo para URL/Email reportado
    url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL o correo electrónico reportado como sospechoso"
    )
    
    incident_type = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text="Tipo de incidente (phishing, malware, acceso_sospechoso, etc)"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='medium',
        help_text="Nivel de severidad del incidente"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        help_text="Estado actual del incidente"
    )
    
    # IA - Confianza de la detección
    confidence = models.FloatField(
        default=0.0,
        help_text="Porcentaje de confianza de la detección (0-1)",
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )
    
    # IA - Tipo de amenaza detectada
    threat_type = models.CharField(
        max_length=100,
        default='unknown',
        help_text="Tipo de amenaza detectada por IA"
    )
    
    # Timestamps
    detected_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora de detección"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de creación del registro"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha de resolución"
    )
    
    # Log de auditoría
    reported_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='reported_incidents',
        help_text="Usuario que reportó el incidente"
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents',
        help_text="Usuario analista asignado para investigar"
    )
    notes = models.TextField(
        blank=True,
        default="",
        help_text="Notas de investigación"
    )
    
    # Información del log
    log_source = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Fuente del log (ej: syslog, firewall, aplicación)"
    )
    ip_source = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP origen del evento"
    )
    ip_destination = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP destino del evento"
    )
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = "Incidente"
        verbose_name_plural = "Incidentes"
        indexes = [
            models.Index(fields=['status', '-detected_at']),
            models.Index(fields=['severity', '-detected_at']),
            models.Index(fields=['confidence']),
        ]
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.title} - {self.status}"
    
    def get_severity_display_html(self):
        """Retorna HTML para mostrar severidad con color"""
        colors = {
            'low': 'green',
            'medium': 'yellow',
            'high': 'orange',
            'critical': 'red',
        }
        color = colors.get(self.severity, 'gray')
        return f'<span style="color: {color}; font-weight: bold;">{self.get_severity_display()}</span>'
    
    def is_critical(self):
        """Verifica si es crítico"""
        return self.severity == 'critical' and self.confidence > 0.8
