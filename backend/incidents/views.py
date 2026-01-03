"""
🚨 VIEWS DE INCIDENTES - TESIS CIBERSEGURIDAD
Ryan Gallegos Mera - PUCEI
Última actualización: 02 de Enero, 2026
"""

from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from .models import Incident
from .serializers import IncidentSerializer
from ia_classifier.classifier import IncidentClassifier


# ========================================
# 🔥 NUEVO: GET INCIDENTES POR ROL
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_incidents(request):
    """
    📊 Obtiene incidentes según el rol del usuario
    """
    user = request.user
    user_role = user.role
    
    print(f"\n{'='*60}")
    print(f"🔍 GET MY INCIDENTS - Usuario: {user.username}, Rol: {user_role}")
    print(f"{'='*60}")
    
    try:
        # Filtrar según el rol
        if user_role == 'admin':
            incidents = Incident.objects.all().order_by('-created_at')
            print(f"✅ Admin - {incidents.count()} incidentes totales")
        
        elif user_role == 'analyst':
            incidents = Incident.objects.filter(assigned_to=user).order_by('-created_at')
            print(f"✅ Analyst - {incidents.count()} incidentes asignados")
        
        elif user_role == 'employee':
            incidents = Incident.objects.filter(reported_by=user).order_by('-created_at')
            print(f"✅ Employee - {incidents.count()} incidentes reportados")
            
            # Debug: mostrar IDs de incidentes encontrados
            if incidents.exists():
                ids = [inc.id for inc in incidents]
                print(f"   IDs encontrados: {ids}")
        
        else:
            print(f"❌ Rol no reconocido: {user_role}")
            return Response(
                {'error': 'Rol no reconocido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        print(f"📊 Intentando serializar {incidents.count()} incidentes...")
        
        # Serializar y devolver
        serializer = IncidentSerializer(incidents, many=True, context={'request': request})
        
        print(f"✅ Serialización exitosa - Retornando {len(serializer.data)} items")
        print(f"{'='*60}\n")
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"❌ ERROR FATAL en get_my_incidents:")
        print(f"   Tipo: {type(e).__name__}")
        print(f"   Mensaje: {str(e)}")
        import traceback
        print(f"   Traceback completo:")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return Response(
            {'error': f'Error al obtener incidentes: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========================================
# 📊 ENDPOINT DE ESTADÍSTICAS POR ROL
# ========================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """
    📈 Obtiene estadísticas personalizadas por rol
    """
    user = request.user
    user_role = user.role
    
    try:
        # Obtener incidentes según rol
        if user_role == 'admin':
            incidents = Incident.objects.all()
        elif user_role == 'analyst':
            incidents = Incident.objects.filter(assigned_to=user)
        else:  # employee
            incidents = Incident.objects.filter(reported_by=user)
        
        # Estadísticas básicas
        stats = {
            'role': user_role,
            'total': incidents.count(),
            'critical': incidents.filter(severity='critical').count(),
            'high': incidents.filter(severity='high').count(),
            'medium': incidents.filter(severity='medium').count(),
            'low': incidents.filter(severity='low').count(),
            'open': incidents.filter(status='new').count(),
            'in_progress': incidents.filter(status='in_progress').count(),
            'closed': incidents.filter(status='resolved').count(),
        }
        
        # Confianza promedio
        avg_confidence = incidents.aggregate(Avg('confidence'))['confidence__avg'] or 0
        stats['average_confidence'] = round(avg_confidence * 100, 2)
        
        # ESTADÍSTICAS EXTRAS PARA ADMIN
        if user_role == 'admin':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            stats['admin_extra'] = {
                'total_users': User.objects.count(),
                'total_analysts': User.objects.filter(role='analyst').count(),
                'total_employees': User.objects.filter(role='employee').count(),
                'critical_unresolved': incidents.filter(
                    severity='critical',
                    status__in=['new', 'in_progress']
                ).count(),
            }
        
        # ESTADÍSTICAS EXTRAS PARA ANALYST
        elif user_role == 'analyst':
            stats['analyst_extra'] = {
                'pending_review': incidents.filter(status='new').count(),
                'assigned_to_me': incidents.filter(status='in_progress').count(),
                'resolved_by_me': incidents.filter(status='resolved').count(),
            }
        
        # ESTADÍSTICAS EXTRAS PARA EMPLOYEE
        elif user_role == 'employee':
            stats['employee_extra'] = {
                'my_open': incidents.filter(status='new').count(),
                'my_resolved': incidents.filter(status='resolved').count(),
                'total_reported': incidents.count(),
            }
        
        return Response(stats, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': f'Error: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ========================================
# 🚨 CRUD BÁSICO
# ========================================

class IncidentListCreateView(generics.ListCreateAPIView):
    """
    GET: Lista incidentes
    POST: Crea un nuevo incidente
    """
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Incident.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Guarda el incidente con clasificación automática de IA
        Y lo asigna automáticamente al primer analista disponible
        """
        # Obtener datos del incidente
        description = self.request.data.get('description', '')
        url = self.request.data.get('url', '')
        threat_type = self.request.data.get('threat_type', 'phishing')
        
        # Combinar URL y descripción para mejor análisis
        text_to_analyze = f"{url} {description}"
        
        # ✅ CLASIFICACIÓN CON IA (con manejo de errores)
        try:
            classifier = IncidentClassifier()
            result = classifier.classify(text_to_analyze, threat_type)
            
            # Verificar si retorna tupla (severity, confidence) o solo severity
            if isinstance(result, tuple) and len(result) == 2:
                severity, confidence = result
            elif isinstance(result, tuple) and len(result) == 1:
                severity = result[0]
                confidence = 0.75
            else:
                # Si es un string directo
                severity = result
                confidence = 0.75
            
        except Exception as e:
            print(f"⚠️ Error en clasificador IA: {e}")
            severity = 'medium'
            confidence = 0.5
        
        # 🔥 AUTO-ASIGNAR AL PRIMER ANALISTA DISPONIBLE
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            # Buscar el primer analista activo
            analyst = User.objects.filter(role='analyst', is_active=True).first()
        except Exception as e:
            print(f"⚠️ No se pudo asignar analista: {e}")
            analyst = None
        
        # Guardar incidente con clasificación y asignación
        incident = serializer.save(
            reported_by=self.request.user,
            severity=severity,
            confidence=confidence,
            assigned_to=analyst
        )
        
        print(f"✅ Incidente #{incident.id} creado:")
        print(f"   Severidad: {severity} ({round(confidence*100)}%)")
        print(f"   Asignado a: {analyst.username if analyst else 'Sin asignar'}")


class IncidentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Obtiene un incidente
    PATCH: Actualiza un incidente
    DELETE: Elimina un incidente
    """
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Incident.objects.all()


class DashboardStatsView(APIView):
    """
    📊 Estadísticas del dashboard
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_role = user.role
        
        try:
            # Obtener incidentes según rol
            if user_role == 'admin':
                incidents = Incident.objects.all()
            elif user_role == 'analyst':
                incidents = Incident.objects.filter(assigned_to=user)
            else:  # employee
                incidents = Incident.objects.filter(reported_by=user)
            
            # Estadísticas básicas
            stats = {
                'role': user_role,
                'total': incidents.count(),
                'critical': incidents.filter(severity='critical').count(),
                'high': incidents.filter(severity='high').count(),
                'medium': incidents.filter(severity='medium').count(),
                'low': incidents.filter(severity='low').count(),
                'open': incidents.filter(status='new').count(),
                'in_progress': incidents.filter(status='in_progress').count(),
                'closed': incidents.filter(status='resolved').count(),
            }
            
            avg_confidence = incidents.aggregate(Avg('confidence'))['confidence__avg'] or 0
            stats['average_confidence'] = round(avg_confidence * 100, 2)
            
            if user_role == 'admin':
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                stats['admin_extra'] = {
                    'total_users': User.objects.count(),
                    'total_analysts': User.objects.filter(role='analyst').count(),
                    'total_employees': User.objects.filter(role='employee').count(),
                    'critical_unresolved': incidents.filter(
                        severity='critical',
                        status__in=['new', 'in_progress']
                    ).count(),
                }
            
            elif user_role == 'analyst':
                stats['analyst_extra'] = {
                    'pending_review': incidents.filter(status='new').count(),
                    'assigned_to_me': incidents.filter(status='in_progress').count(),
                    'resolved_by_me': incidents.filter(status='resolved').count(),
                }
            
            elif user_role == 'employee':
                stats['employee_extra'] = {
                    'my_open': incidents.filter(status='new').count(),
                    'my_resolved': incidents.filter(status='resolved').count(),
                    'total_reported': incidents.count(),
                }
            
            return Response(stats, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': f'Error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
