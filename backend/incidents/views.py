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
