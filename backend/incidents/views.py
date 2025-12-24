"""
Views para gestión de incidentes con Django REST Framework
Cada incidente se guarda en la base de datos SQLite
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Incident
from .serializers import IncidentSerializer
import re


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para gestionar incidentes de ciberseguridad
    
    Endpoints disponibles:
    - GET /api/incidents/ - Listar todos
    - POST /api/incidents/ - Crear nuevo
    - GET /api/incidents/{id}/ - Detalle
    - PUT /api/incidents/{id}/ - Actualizar
    - DELETE /api/incidents/{id}/ - Eliminar
    - POST /api/incidents/{id}/analyze/ - Análisis IA
    """
    
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    
    def perform_create(self, serializer):
        """Guardar en BD al crear"""
        serializer.save()
    
    @action(detail=True, methods=['post'], url_path='analyze')
    def analyze(self, request, pk=None):
        """
        Endpoint especial para analizar un incidente ya guardado
        POST /api/incidents/{id}/analyze/
        """
        incident = self.get_object()
        
        # Lógica de análisis
        analysis = self._analyze_incident_logic(incident.description)
        
        # Actualizar incidente con resultado
        incident.ai_recommendation = analysis['recommendation']
        incident.save()
        
        return Response({
            "success": True,
            "incident_id": incident.id,
            "analysis": analysis
        })
    
    @staticmethod
    def _analyze_incident_logic(description: str) -> dict:
        """
        Lógica central de análisis de amenazas
        Retorna: {threat_type, criticality, confidence, recommendation, technical_details}
        """
        desc_lower = description.lower().strip()
        
        # Respuesta por defecto
        threat_type = 'OTRO'
        criticality = 'BAJO'
        recommendation = 'No se identifican incidentes. Continúe con sus funciones habituales.'
        technical_details = 'Ningún síntoma ni patrón asociado a amenazas detectado en la descripción.'
        confidence = 0.85
        
        # Caso: Entrada vacía o irrelevante
        if not desc_lower or desc_lower in [
            'hola', 'buenos días', 'prueba', 'test', 'agua', 'ninguno', 'nada'
        ]:
            threat_type = 'OTRO'
            criticality = 'BAJO'
            recommendation = 'No se detecta amenaza ni riesgo. Puede seguir con su trabajo.'
            technical_details = 'Esta entrada no presenta riesgos de seguridad informática.'
            confidence = 0.95
        
        # Caso: PHISHING (correos maliciosos)
        elif any(word in desc_lower for word in [
            'banco', 'enlace', 'login', 'clave', 'contraseña', 'phishing', 
            'click', 'verificar datos', 'confirmar identidad'
        ]):
            threat_type = 'PHISHING'
            criticality = 'ALTO'
            recommendation = 'No haga clic ni responda. Reporte a TI inmediatamente.'
            technical_details = 'Detectado patrón de probable phishing o intento fraudulento.'
            confidence = 0.92
        
        # Caso: MALWARE (archivos sospechosos)
        elif any(word in desc_lower for word in [
            'descarga', 'archivo', 'malware', 'virus', 'ejecutable', '.exe',
            'ralentización', 'comportamiento extraño'
        ]):
            threat_type = 'MALWARE'
            criticality = 'CRITICO'
            recommendation = 'Aísle su equipo y contacte soporte técnico de inmediato.'
            technical_details = 'Palabras clave vinculadas a software malicioso o infección.'
            confidence = 0.88
        
        # Caso: INGENIERÍA SOCIAL (suplantación)
        elif any(word in desc_lower for word in [
            'transferencia', 'dinero', 'urgente', 'ceo', 'jefe', 'ingeniería social',
            'pretende ser', 'suplantación', 'pago urgente'
        ]):
            threat_type = 'ACCESO_NO_AUTORIZADO'
            criticality = 'CRITICO'
            recommendation = 'Verifique la identidad de la persona. No continúe sin confirmación.'
            technical_details = 'Posible ingeniería social o suplantación de autoridad detectada.'
            confidence = 0.90
        
        # Caso: RANSOMWARE (cifrado malicioso)
        elif any(word in desc_lower for word in [
            'ransomware', 'cifrado', 'rescate', 'archivos bloqueados', 'acceso denegado'
        ]):
            threat_type = 'RANSOMWARE'
            criticality = 'CRITICO'
            recommendation = 'Aísle el sistema ahora. NO pague rescate. Contacte TI urgente.'
            technical_details = 'Indicadores de posible ataque ransomware con cifrado.'
            confidence = 0.94
        
        return {
            'threat_type': threat_type,
            'criticality': criticality,
            'confidence': confidence,
            'recommendation': recommendation,
            'technical_details': technical_details
        }
    
    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """
        Endpoint para estadísticas del dashboard
        GET /api/incidents/stats/
        """
        total = Incident.objects.count()
        critical = Incident.objects.filter(criticality='CRITICO').count()
        resolved = Incident.objects.filter(resolved=True).count()
        pending = Incident.objects.filter(resolved=False).count()
        
        # Contar por tipo
        incidents_by_type = {}
        for incident in Incident.objects.all():
            threat_type = incident.threat_type
            incidents_by_type[threat_type] = incidents_by_type.get(threat_type, 0) + 1
        
        return Response({
            'total_incidents': total,
            'critical_incidents': critical,
            'resolved_incidents': resolved,
            'pending_incidents': pending,
            'incidents_by_type': incidents_by_type,
        })
