from django.db import models
from django.contrib.auth.models import User

class Incident(models.Model):
    # Tabla para guardar los incidentes (archivos o links reportados)
    
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
        ('image', 'Imagen'),
    ]
    
    # Informacion basica
    incident_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)
    attached_file = models.FileField(upload_to='incidents/', blank=True, null=True)
    description = models.TextField(blank=True, default='')
    
    # Resultados del analisis (VirusTotal, IA, etc)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVELS, default='UNKNOWN')
    virustotal_result = models.JSONField(blank=True, null=True)
    phishtank_result = models.JSONField(blank=True, null=True)
    metadefender_result = models.JSONField(blank=True, null=True)
    gemini_analysis = models.TextField(blank=True, default='')
    analysis_result = models.JSONField(blank=True, null=True) # Full analysis snapshot
    
    # Datos de control
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    analyst_notes = models.TextField(blank=True, default='')  # Notas del tecnico
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Incidente'
        verbose_name_plural = 'Incidentes'
    
    def __str__(self):
        return f"Incidente #{self.id} - {self.get_risk_level_display()}"

class IncidentNote(models.Model):
    # Notas internas para analistas
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Nota de Incidente'
        verbose_name_plural = 'Notas de Incidentes'
        
    def __str__(self):
        return f"Nota en #{self.incident.id} por {self.author.username}"

import hashlib
from django.utils import timezone

class AnalysisCache(models.Model):
    # Guardo aqui los analisis antiguos para no gastar peticiones a la API
    # Si alguien busca lo mismo, se lo doy de aqui rapido
    
    TYPE_CHOICES = [
        ('url', 'URL'),
        ('file', 'Archivo'),
    ]
    
    # Identificador único
    cache_key = models.CharField(max_length=64, unique=True, db_index=True)
    analysis_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    
    # Datos originales
    url = models.URLField(blank=True, null=True)
    file_hash = models.CharField(max_length=64, blank=True, null=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    
    # Resultados cacheados
    virustotal_result = models.JSONField(blank=True, null=True)
    metadefender_result = models.JSONField(blank=True, null=True)
    google_sb_result = models.JSONField(blank=True, null=True)
    gemini_result = models.JSONField(blank=True, null=True)
    
    risk_level = models.CharField(max_length=10, blank=True, null=True)
    positives = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    source = models.CharField(max_length=50, blank=True, null=True)
    
    # Control de caché
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    hits = models.IntegerField(default=0)
    
    class Meta:
        verbose_name = 'Cache de Analisis'
        verbose_name_plural = 'Cache de Analisis'
        ordering = ['-created_at']
    
    @staticmethod
    def generate_cache_key(analysis_type, identifier):
        """
        Genera clave única para caché.
        identifier: URL o hash SHA-256 del archivo
        """
        key_string = f"{analysis_type}:{identifier}"
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    @staticmethod
    def get_cached(analysis_type, identifier):
        """
        Busca resultado cacheado válido.
        Retorna None si no existe o expiró.
        """
        cache_key = AnalysisCache.generate_cache_key(analysis_type, identifier)
        
        try:
            cache = AnalysisCache.objects.get(
                cache_key=cache_key,
                expires_at__gt=timezone.now()
            )
            
            # Incrementar contador de hits
            cache.hits += 1
            cache.save(update_fields=['hits'])
            
            return cache
            
        except AnalysisCache.DoesNotExist:
            return None
    
    @staticmethod
    def store(analysis_type, identifier, results, expiration_hours=24):
        """
        Almacena resultado en caché.
        expiration_hours: Tiempo de vida del caché (default 24h)
        """
        cache_key = AnalysisCache.generate_cache_key(analysis_type, identifier)
        expires_at = timezone.now() + timezone.timedelta(hours=expiration_hours)
        
        cache, created = AnalysisCache.objects.update_or_create(
            cache_key=cache_key,
            defaults={
                'analysis_type': analysis_type,
                'url': results.get('url'),
                'file_hash': results.get('file_hash'),
                'file_name': results.get('file_name'),
                'virustotal_result': results.get('virustotal_result', {}),
                'metadefender_result': results.get('metadefender_result', {}),
                'google_sb_result': results.get('google_sb_result', {}),
                'gemini_result': results.get('gemini_result', {}),
                'risk_level': results.get('risk_level'),
                'positives': results.get('positives', 0),
                'total': results.get('total', 0),
                'source': results.get('source'),
                'expires_at': expires_at,
                'hits': 1 
            }
        )
        
        return cache
