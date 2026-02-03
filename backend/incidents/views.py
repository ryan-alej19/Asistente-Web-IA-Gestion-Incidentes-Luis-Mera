from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Incident
from .serializers import IncidentSerializer
from services.virustotal_service import VirusTotalService
from services.metadefender_service import MetaDefenderService
from services.gemini_service import GeminiService
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_file_preview(request):
    """
    Análisis de archivo con rotación automática VirusTotal -> MetaDefender.
    """
    try:
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({'error': 'No se proporcionó archivo'}, status=400)
        
        logger.info(f"Analizando archivo: {file_obj.name}")
        
        # Intentar con VirusTotal (Principal)
        vt_service = VirusTotalService()
        vt_result = vt_service.analyze_file(file_obj)
        
        source_used = 'VirusTotal'
        vt_success = 'error' not in vt_result and vt_result.get('positives') is not None
        
        # Si VT falla, rotar a MetaDefender (Respaldo)
        if not vt_success:
            logger.warning("VirusTotal no disponible o falló, rotando a MetaDefender...")
            
            md_service = MetaDefenderService()
            md_result = md_service.analyze_file(file_obj)
            
            if 'error' not in md_result:
                vt_result = md_result
                source_used = 'MetaDefender'
                logger.info("MetaDefender respondió exitosamente")
            else:
                # Ambos servicios fallaron
                logger.error("Todos los servicios de análisis fallaron")
                return Response({
                    'risk_level': 'UNKNOWN',
                    'message': 'Servicios no disponibles',
                    'detail': 'No se pudo completar el análisis. Intente más tarde.',
                    'positives': 0,
                    'total': 0
                }, status=503)
        
        # Extraer resultados
        positives = vt_result.get('positives', 0)
        total = vt_result.get('total', 90)
        
        logger.info(f"Resultado: {positives}/{total} detectores ({source_used})")
        
        # Calcular nivel de riesgo
        if positives > 15:
            risk = 'CRITICAL'
            message = 'PELIGRO'
        elif positives > 5:
            risk = 'HIGH'
            message = 'Alto riesgo'
        elif positives > 0:
            risk = 'MEDIUM'
            message = 'Sospechoso'
        else:
            risk = 'LOW'
            message = 'SEGURO'
        
        detail = f'{positives} de {total} motores detectaron amenazas' if positives > 0 else f'Analizado por {total} motores - Sin amenazas'
        
        # Análisis explicativo con Gemini (Opcional)
        gemini_explicacion = ''
        gemini_recomendacion = ''
        try:
            gemini_service = GeminiService()
            gemini_result = gemini_service.explain_threat(positives, total, 'file')
            gemini_explicacion = gemini_result.get('explicacion', '')
            gemini_recomendacion = gemini_result.get('recomendacion', '')
        except Exception as e:
            logger.warning(f"Gemini no disponible: {e}")
        
        return Response({
            'risk_level': risk,
            'message': message,
            'detail': detail,
            'positives': positives,
            'total': total,
            'source': source_used,
            'gemini_explicacion': gemini_explicacion,
            'gemini_recomendacion': gemini_recomendacion
        })
        
    except Exception as e:
        logger.error(f"Error en análisis de archivo: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_url_preview(request):
    """
    Análisis de URL usando VirusTotal y Gemini.
    """
    try:
        url = request.data.get('url')
        
        if not url:
            return Response({'error': 'No se proporcionó URL'}, status=400)
        
        logger.info(f"Analizando URL: {url}")
        
        # VirusTotal
        vt_service = VirusTotalService()
        vt_result = vt_service.analyze_url(url)
        
        source_used = 'VirusTotal'
        
        # Calcular riesgo
        positives = vt_result.get('positives', 0)
        total = vt_result.get('total', 90)
        
        if positives > 5:
            risk = 'CRITICAL'
            message = 'URL peligrosa detectada'
        elif positives > 0:
            risk = 'MEDIUM'
            message = 'URL sospechosa'
        else:
            risk = 'LOW'
            message = 'URL segura'
            
        detail = f'{positives} de {total} motores detectaron amenazas' if positives > 0 else f'Analizado por {total} motores - Sin amenazas'

        # Gemini
        gemini_explicacion = ''
        gemini_recomendacion = ''
        try:
            gemini_service = GeminiService()
            gemini_result = gemini_service.explain_threat(positives, total, 'url')
            gemini_explicacion = gemini_result.get('explicacion', '')
            gemini_recomendacion = gemini_result.get('recomendacion', '')
        except Exception as e:
            logger.warning(f"Gemini no disponible: {e}")
        
        return Response({
            'risk_level': risk,
            'message': message,
            'detail': detail,
            'virustotal': vt_result,
            'source': source_used,
            'gemini_explicacion': gemini_explicacion,
            'gemini_recomendacion': gemini_recomendacion
        })
        
    except Exception as e:
        logger.error(f"Error en análisis de URL: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_incident(request):
    """
    Crea incidente guardando los resultados del análisis.
    """
    try:
        incident_type = request.data.get('incident_type')
        
        incident = Incident.objects.create(
            incident_type=incident_type,
            url=request.data.get('url'),
            description=request.data.get('description', ''),
            reported_by=request.user,
            status='pending'
        )
        
        vt_result = {}
        risk = 'UNKNOWN'
        
        if incident_type == 'file' and request.FILES.get('file'):
            incident.attached_file = request.FILES.get('file')
            
            # VirusTotal
            vt_service = VirusTotalService()
            vt_result = vt_service.analyze_file(incident.attached_file)
            
            # Rotación a MetaDefender si falla VT
            if 'error' in vt_result:
                 md_service = MetaDefenderService()
                 md_result = md_service.analyze_file(incident.attached_file)
                 if 'error' not in md_result:
                     vt_result = md_result
            
            incident.virustotal_result = vt_result 
            
            positives = vt_result.get('positives', 0)
            if positives > 15:
                risk = 'CRITICAL'
            elif positives > 5:
                risk = 'HIGH'
            elif positives > 0:
                risk = 'MEDIUM'
            else:
                risk = 'LOW'
                
        elif incident_type == 'url':
            vt_service = VirusTotalService()
            vt_result = vt_service.analyze_url(incident.url)
            incident.virustotal_result = vt_result
            
            positives = vt_result.get('positives', 0)
            if positives > 5:
                risk = 'CRITICAL'
            elif positives > 0:
                risk = 'MEDIUM'
            else:
                risk = 'LOW'
        
        incident.risk_level = risk
        
        # Guardar análisis de Gemini si es posible
        try:
            gemini_service = GeminiService()
            # Usamos explain_threat para obtener el JSON,
            # luego podemos guardar la explicación o recomendación en el campo de texto
            total = vt_result.get('total', 90)
            gemini_result = gemini_service.explain_threat(positives, total, incident_type)
            incident.gemini_analysis = gemini_result.get('explicacion', '')
        except:
             pass

        incident.save()
        
        serializer = IncidentSerializer(incident)
        return Response(serializer.data, status=201)
        
    except Exception as e:
        logger.error(f"Error creando incidente: {e}")
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_incidents(request):
    """
    Lista incidentes según rol.
    """
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        
        if user_role in ['admin', 'analyst']:
            incidents = Incident.objects.all()
        else:
            incidents = Incident.objects.filter(reported_by=request.user)
        
        serializer = IncidentSerializer(incidents, many=True)
        return Response(serializer.data)
    except Exception as e:
         logger.error(f"Error listando incidentes: {e}")
         return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_detail(request, incident_id):
    """
    Detalle de incidente.
    """
    try:
        incident = Incident.objects.get(id=incident_id)
        
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'

        if user_role == 'employee' and incident.reported_by != request.user:
            return Response({'error': 'No autorizado'}, status=403)
        
        serializer = IncidentSerializer(incident)
        return Response(serializer.data)
        
    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)
