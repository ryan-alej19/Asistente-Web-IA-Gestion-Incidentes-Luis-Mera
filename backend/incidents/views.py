"""
Views para gestión de incidentes con Django REST Framework
Cada incidente se guarda en la base de datos SQLite
"""
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from django.utils import timezone
from django.contrib.auth.models import User


from .models import Incident
from .serializers import IncidentSerializer, IncidentListSerializer, IncidentCreateSerializer
from ia_classifier.classifier import IncidentClassifier
from ia_classifier.classifier import IncidentClassifier  # ← AGREGAR ESTO


# ============================================
# PAGINACIÓN ESTÁNDAR
# ============================================

class StandardPagination(PageNumberPagination):
    """Paginación estándar: 20 incidentes por página"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


# ============================================
# VIEWSET PRINCIPAL DE INCIDENTES
# ============================================

class IncidentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para gestionar incidentes de ciberseguridad
    
    Endpoints disponibles:
    - GET /api/incidents/ - Listar todos
    - POST /api/incidents/ - Crear nuevo
    - GET /api/incidents/{id}/ - Obtener detalle
    - PUT /api/incidents/{id}/ - Actualizar completo
    - PATCH /api/incidents/{id}/ - Actualizar parcial
    - DELETE /api/incidents/{id}/ - Eliminar
    
    Acciones personalizadas:
    - POST /api/incidents/{id}/resolve/ - Marcar como resuelto
    - POST /api/incidents/{id}/assign/ - Asignar a usuario
    - GET /api/incidents/critical/ - Obtener solo críticos
    - GET /api/incidents/statistics/ - Estadísticas
    - GET /api/incidents/recent/ - Últimas 24 horas
    - POST /api/incidents/bulk_resolve/ - Resolver múltiples
    """
    
    queryset = Incident.objects.select_related('assigned_to').order_by('-detected_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
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
    
    def create(self, request, *args, **kwargs):
        """
        Crear nuevo incidente con clasificación automática por IA
        
        POST /api/incidents/
        
        Body esperado:
        {
            "title": "Incidente de seguridad",
            "description": "Descripción detallada",
            "threat_type": "phishing",  // phishing, malware, acceso_sospechoso, otro
            "severity": "medium"  // Opcional - será calculado por IA
        }
        """
        
        # Obtener datos del request
        title = request.data.get('title', '')
        description = request.data.get('description', '')
        threat_type = request.data.get('threat_type', 'otro')
        
        # Validación básica
        if not title or not description:
            return Response(
                {'error': 'Título y descripción son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✨ LLAMAR AL CLASIFICADOR IA ✨
        classifier = IncidentClassifier()
        severity, confidence_score = classifier.classify(description, threat_type)
        
        # Crear el incidente con severidad asignada automáticamente
        incident = Incident.objects.create(
            title=title,
            description=description,
            threat_type=threat_type,
            severity=severity,
            confidence=confidence_score,
            status='new',
            detected_at=timezone.now()
        )
        
        # Retornar respuesta completa
        serializer = IncidentSerializer(incident)
        return Response(
            {
                'status': 'success',
                'message': f'Incidente creado. Severidad asignada: {severity}',
                'incident': serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    def perform_update(self, serializer):
        """Hook que se ejecuta al actualizar"""
        serializer.save()
    
    # ============================================
    # ACCIONES PERSONALIZADAS
    # ============================================
    
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
        
        serializer = IncidentSerializer(incident)
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
            
            serializer = IncidentSerializer(incident)
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
            serializer = IncidentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = IncidentSerializer(critical_incidents, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Acción: Obtener estadísticas de incidentes
        GET /api/incidents/statistics/
        """
        total = self.queryset.count()
        by_severity = self.queryset.values('severity').annotate(count=Count('id'))
        by_status = self.queryset.values('status').annotate(count=Count('id'))
        by_type = self.queryset.values('threat_type').annotate(count=Count('id'))
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
            'by_type': list(by_type),
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
            serializer = IncidentSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = IncidentSerializer(recent_incidents, many=True)
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
# ENDPOINT ALTERNATIVO (compatibilidad)
# ============================================

@api_view(['POST'])
def create_incident_report_from_form(request):
    """
    Endpoint alternativo para recibir reportes del formulario
    
    POST /api/create-report/
    
    Body esperado:
    {
        "description": "Descripción del incidente",
        "threat_type": "phishing"
    }
    """
    try:
        description = request.data.get('description')
        threat_type = request.data.get('threat_type', 'otro')
        
        if not description or description.strip() == '':
            return Response(
                {
                    'status': 'error',
                    'message': 'La descripción del incidente es requerida'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Usar clasificador IA
        classifier = IncidentClassifier()
        severity, confidence_score = classifier.classify(description, threat_type)
        
        # Crear incidente
        incident = Incident.objects.create(
            title=f"Reporte: {threat_type.upper()}",
            description=description,
            threat_type=threat_type,
            severity=severity,
            confidence=confidence_score,
            status='new',
            detected_at=timezone.now()
        )
        
        return Response(
            {
                'status': 'success',
                'message': 'Incidente reportado exitosamente',
                'incident_id': incident.id,
                'severity': severity,
                'confidence': confidence_score,
                'incident': {
                    'id': incident.id,
                    'title': incident.title,
                    'description': incident.description,
                    'severity': incident.severity,
                    'confidence': incident.confidence,
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
