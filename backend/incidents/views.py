"""
🛡️ VIEWS - TESIS CIBERSEGURIDAD
Ryan Gallegos Mera - PUCESI
Última actualización: 03 de Enero, 2026
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Incident
from .serializers import IncidentSerializer
from .virustotal_service import VirusTotalService, analyze_with_gemini
import json
from ia_classifier.classifier import ThreatClassifier

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_incident(request):
    """
    Crear un nuevo incidente con análisis de VirusTotal + Gemini AI
    """
    try:
        print(f"\n{'='*60}")
        print(f"📝 CREANDO NUEVO INCIDENTE")
        print(f"Usuario: {request.user.username}")
        print(f"{'='*60}")
        
        data = request.data
        
        # Validar datos requeridos
        if not data.get('incident_type'):
            return Response({
                'error': 'El tipo de incidente es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not data.get('description'):
            return Response({
                'error': 'La descripción es requerida'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 1. Crear el incidente
        incident = Incident.objects.create(
            user=request.user,
            incident_type=data['incident_type'],
            description=data['description'],
            url=data.get('url', ''),
            status='Nuevo'
        )
        
        print(f"✅ Incidente creado - ID: {incident.id}")
        
        # 2. Analizar con VirusTotal (si hay URL)
        virustotal_result = None
        if data.get('url'):
            print(f"🔍 Analizando URL con VirusTotal...")
            vt_service = VirusTotalService()
            virustotal_result = vt_service.analyze_url(data['url'])
            
            # Guardar resultado en el incidente
            incident.virustotal_analysis = json.dumps(virustotal_result)
            print(f"✅ VirusTotal completado")
        
        # 3. Analizar con Gemini AI
        print(f"🤖 Analizando con Gemini AI...")
        gemini_result = analyze_with_gemini({
            'incident_type': data['incident_type'],
            'description': data['description'],
            'url': data.get('url', ''),
            'virustotal_result': virustotal_result
        })
        
        # Guardar resultado de Gemini
        incident.gemini_analysis = json.dumps(gemini_result)
        
        # Actualizar nivel de riesgo según Gemini
        if gemini_result.get('risk_level'):
            incident.risk_level = gemini_result['risk_level']
        
        # Actualizar confianza IA
        if gemini_result.get('confidence'):
            incident.ai_confidence = gemini_result['confidence']
        
        incident.save()
        print(f"✅ Gemini AI completado")
        print(f"{'='*60}\n")
        
        # 4. Serializar y retornar respuesta
        serializer = IncidentSerializer(incident)
        
        return Response({
            'success': True,
            'message': 'Incidente creado y analizado correctamente',
            'incident': serializer.data,
            'virustotal': virustotal_result,
            'gemini': gemini_result
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        print(f"❌ ERROR AL CREAR INCIDENTE: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return Response({
            'error': f'Error al crear incidente: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_incidents(request):
    """
    Listar incidentes del usuario
    """
    try:
        user = request.user
        
        # Si es admin o analista, ver todos los incidentes
        if user.role in ['admin', 'analyst']:
            incidents = Incident.objects.all().order_by('-created_at')
        else:
            # Si es empleado, solo ver sus incidentes
            incidents = Incident.objects.filter(user=user).order_by('-created_at')
        
        serializer = IncidentSerializer(incidents, many=True)
        
        return Response({
            'success': True,
            'incidents': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_incident_detail(request, incident_id):
    """
    Obtener detalle de un incidente específico
    """
    try:
        incident = Incident.objects.get(id=incident_id)
        
        # Verificar permisos
        if request.user.role not in ['admin', 'analyst'] and incident.user != request.user:
            return Response({
                'error': 'No tienes permiso para ver este incidente'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = IncidentSerializer(incident)
        
        # Parsear análisis JSON
        virustotal_data = None
        gemini_data = None
        
        if incident.virustotal_analysis:
            try:
                virustotal_data = json.loads(incident.virustotal_analysis)
            except:
                pass
        
        if incident.gemini_analysis:
            try:
                gemini_data = json.loads(incident.gemini_analysis)
            except:
                pass
        
        return Response({
            'success': True,
            'incident': serializer.data,
            'virustotal': virustotal_data,
            'gemini': gemini_data
        }, status=status.HTTP_200_OK)
        
    except Incident.DoesNotExist:
        return Response({
            'error': 'Incidente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_incident_status(request, incident_id):
    """
    Actualizar estado de un incidente (solo analistas y admins)
    """
    try:
        user = request.user
        
        # Verificar permisos
        if user.role not in ['admin', 'analyst']:
            return Response({
                'error': 'No tienes permiso para actualizar incidentes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        incident = Incident.objects.get(id=incident_id)
        
        # Actualizar campos permitidos
        if 'status' in request.data:
            incident.status = request.data['status']
        
        if 'analyst_notes' in request.data:
            incident.analyst_notes = request.data['analyst_notes']
        
        if 'assigned_to' in request.data:
            incident.assigned_to = request.data['assigned_to']
        
        incident.save()
        
        serializer = IncidentSerializer(incident)
        
        return Response({
            'success': True,
            'message': 'Incidente actualizado correctamente',
            'incident': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Incident.DoesNotExist:
        return Response({
            'error': 'Incidente no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """
    Obtener estadísticas para el dashboard
    """
    try:
        user = request.user
        
        # Si es admin/analista, ver todas las estadísticas
        if user.role in ['admin', 'analyst']:
            incidents = Incident.objects.all()
        else:
            # Si es empleado, solo sus estadísticas
            incidents = Incident.objects.filter(user=user)
        
        # Contar por estado
        stats = {
            'total': incidents.count(),
            'nuevo': incidents.filter(status='Nuevo').count(),
            'en_proceso': incidents.filter(status='En Proceso').count(),
            'resuelto': incidents.filter(status='Resuelto').count(),
            'cerrado': incidents.filter(status='Cerrado').count(),
        }
        
        # Contar por nivel de riesgo
        stats['por_riesgo'] = {
            'bajo': incidents.filter(risk_level='Bajo').count(),
            'medio': incidents.filter(risk_level='Medio').count(),
            'alto': incidents.filter(risk_level='Alto').count(),
            'critico': incidents.filter(risk_level='Crítico').count(),
        }
        
        return Response({
            'success': True,
            'stats': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
