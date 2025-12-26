<<<<<<< HEAD
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.decorators import action  


from .models import Incident
from .serializers import (
    IncidentSerializer,
    IncidentListSerializer,
    IncidentCreateSerializer
)


class StandardPagination(PageNumberPagination):
    """Paginación estándar: 20 incidentes por página"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para gestionar incidentes de seguridad
    
    Endpoints:
    - GET /api/incidents/ - Listar todos
    - POST /api/incidents/ - Crear nuevo
    - GET /api/incidents/{id}/ - Obtener detalle
    - PUT /api/incidents/{id}/ - Actualizar completo
    - PATCH /api/incidents/{id}/ - Actualizar parcial
    - DELETE /api/incidents/{id}/ - Eliminar
    
    Acciones personalizadas:
    - POST /api/incidents/{id}/resolve/ - Marcar como resuelto
    - POST /api/incidents/{id}/assign/ - Asignar a usuario
    - POST /api/incidents/{id}/mark-as-false-positive/ - Marcar como falsa alarma
    - GET /api/incidents/critical/ - Obtener solo críticos
    - GET /api/incidents/statistics/ - Estadísticas
    """
    
    queryset = Incident.objects.select_related('assigned_to').order_by('-detected_at')
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Filtros disponibles
    filterset_fields = ['severity', 'status', 'threat_type', 'assigned_to']
    
    # Búsqueda
    search_fields = ['title', 'description', 'threat_type', 'ip_source', 'ip_destination']
    
    # Ordenamiento
    ordering_fields = ['detected_at', 'severity', 'confidence', 'created_at']
    ordering = ['-detected_at']
    
    def get_serializer_class(self):
        """Retorna diferente serializer según la acción"""
        if self.action == 'list':
            return IncidentListSerializer
        elif self.action == 'create':
            return IncidentCreateSerializer
        return IncidentSerializer
    
    def perform_create(self, serializer):
        """Hook que se ejecuta al crear un incidente"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Hook que se ejecuta al actualizar"""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Acción: Marcar incidente como resuelto
        POST /api/incidents/{id}/resolve/
        """
        incident = self.get_object()
        incident.status = 'resolved'
        incident.resolved_at = timezone.now()
        incident.save()
        
        serializer = self.get_serializer(incident)
        return Response(
            {
                'status': 'success',
                'message': f'Incidente {incident.id} marcado como resuelto',
                'incident': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Acción: Asignar incidente a un usuario
        POST /api/incidents/{id}/assign/
        Body: {"user_id": 1}
        """
        incident = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response(
                {'error': 'user_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(id=user_id)
            incident.assigned_to = user
            incident.save()
            
            serializer = self.get_serializer(incident)
            return Response(
                {
                    'status': 'success',
                    'message': f'Incidente asignado a {user.username}',
                    'incident': serializer.data
                },
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'error': f'Usuario con ID {user_id} no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_false_positive(self, request, pk=None):
        """
        Acción: Marcar incidente como falsa alarma
        POST /api/incidents/{id}/mark-as-false-positive/
        """
        incident = self.get_object()
        incident.status = 'false_positive'
        incident.save()
        
        serializer = self.get_serializer(incident)
        return Response(
            {
                'status': 'success',
                'message': f'Incidente {incident.id} marcado como falsa alarma',
                'incident': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'])
    def critical(self, request):
        """
        Acción: Obtener solo incidentes críticos
        GET /api/incidents/critical/
        """
        critical_incidents = self.queryset.filter(
            severity='critical',
            confidence__gte=0.8
        )
        
        page = self.paginate_queryset(critical_incidents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(critical_incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Acción: Obtener estadísticas de incidentes
        GET /api/incidents/statistics/
        """
        from django.db.models import Count, Avg
        
        total = self.queryset.count()
        by_severity = self.queryset.values('severity').annotate(count=Count('id'))
        by_status = self.queryset.values('status').annotate(count=Count('id'))
        avg_confidence = self.queryset.aggregate(Avg('confidence'))['confidence__avg'] or 0
        
        # Críticos sin resolver
        unresolved_critical = self.queryset.filter(
            severity='critical',
            status__in=['new', 'under_review', 'in_progress']
        ).count()
        
        return Response({
            'total_incidents': total,
            'by_severity': list(by_severity),
            'by_status': list(by_status),
            'average_confidence': round(avg_confidence * 100, 2),
            'unresolved_critical': unresolved_critical,
        })
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Acción: Obtener incidentes recientes (últimas 24 horas)
        GET /api/incidents/recent/
        """
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(hours=24)
        recent_incidents = self.queryset.filter(detected_at__gte=cutoff_time)
        
        page = self.paginate_queryset(recent_incidents)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recent_incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_resolve(self, request):
        """
        Acción: Resolver múltiples incidentes a la vez
        POST /api/incidents/bulk_resolve/
        Body: {"incident_ids": [1, 2, 3]}
        """
        incident_ids = request.data.get('incident_ids', [])
        
        if not incident_ids:
            return Response(
                {'error': 'incident_ids es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated = Incident.objects.filter(id__in=incident_ids).update(
            status='resolved',
            resolved_at=timezone.now()
        )
        
        return Response({
            'status': 'success',
            'message': f'{updated} incidentes marcados como resueltos',
            'updated_count': updated
        })


# ============================================
# NUEVO: ENDPOINT PARA EL FORMULARIO FRONTEND
# ============================================

@api_view(['POST'])
def create_incident_report_from_form(request):
    """
    Endpoint para recibir reportes del formulario IncidentReporter.js
    
    POST /api/create-report/
    
    Body esperado:
    {
        "description": "Descripción del incidente",
        "severity": "low",  // low, medium, high, critical
        "threat_type": "malware"  // opcional
    }
    """
    try:
        # Obtener datos del request
        description = request.data.get('description')
        severity = request.data.get('severity', 'low')
        threat_type = request.data.get('threat_type', 'unknown')
        
        # Validar que haya descripción
        if not description or description.strip() == '':
            return Response(
                {
                    'status': 'error',
                    'message': 'La descripción del incidente es requerida'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar severity
        valid_severities = ['low', 'medium', 'high', 'critical']
        if severity not in valid_severities:
            return Response(
                {
                    'status': 'error',
                    'message': f'Severidad inválida. Use: {", ".join(valid_severities)}'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el incidente
        incident = Incident.objects.create(
            title=f"Reporte: {threat_type.upper()}",
            description=description,
            severity=severity,
            threat_type=threat_type,
            status='new',
            detected_at=timezone.now(),
            confidence=0.5,  # Valor por defecto
            # Los campos de IP puedes dejarlos vacíos o obtenerlos del request si deseas
        )
        
        return Response(
            {
                'status': 'success',
                'message': 'Incidente reportado exitosamente',
                'incident_id': incident.id,
                'incident': {
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'severity': incident.severity,
                    'status': incident.status,
                    'created_at': incident.created_at
                }
            },
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {
                'status': 'error',
                'message': f'Error al crear el incidente: {str(e)}'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
=======
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
>>>>>>> 0ac16d3a1f6351a133051af9b8c67e4f08d6cd60
