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

@permission_classes([IsAuthenticated])
def analyze_file_preview(request):
    """
    Funcion para analizar archivos.
    Primero usa VirusTotal y si falla, usa MetaDefender.
    """
    try:
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({'error': 'No se proporcionó archivo'}, status=400)
        
        logger.info(f"Analizando archivo: {file_obj.name}")
        
        # Intentamos primero con VirusTotal con proteccion anti-crash
        vt_result = {}
        vt_success = False
        
        try:
            vt_service = VirusTotalService()
            vt_result = vt_service.analyze_file(file_obj)
            
            # Verificamos si hubo error o cuota excedida
            if 'error' in vt_result:
                raise Exception(vt_result['error'])
                
            vt_success = True
            source_used = 'VirusTotal'
            
        except Exception as e:
            logger.info(f"[INFO] Fallo VirusTotal ({e}). Cambiando a motor de respaldo (MetaDefender)...")
            vt_success = False

        # Si VirusTotal falla, probamos con MetaDefender (Fallback Automatico)
        if not vt_success:
            try:
                md_service = MetaDefenderService()
                md_result = md_service.analyze_file(file_obj)
                
                if 'error' not in md_result:
                    vt_result = md_result
                    source_used = 'MetaDefender'
                    logger.info("MetaDefender funciono correctamente")
                else:
                    raise Exception(md_result['error'])
            except Exception as e:
                # Si ambos fallan
                logger.error(f"Todos los servicios fallaron: {e}")
                return Response({
                    'risk_level': 'UNKNOWN',
                    'message': 'Servicios no disponibles',
                    'detail': 'No se pudo completar el analisis. Protocolo de contingencia activado.',
                    'positives': 0,
                    'total': 0
                }, status=503)
        
        # Obtenemos los resultados
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
        
        # Variables para el resultado unificado
        positives = 0
        total = 0
        risk = 'UNKNOWN'
        message = ''
        detail = ''
        source_used = ''
        vt_data = {} # Para guardar raw data si existe
        
        # 1. Intentamos con VirusTotal
        vt_result = {}
        vt_success = False
        
        try:
            vt_service = VirusTotalService()
            vt_result = vt_service.analyze_url(url)
            
            if 'error' in vt_result:
                 raise Exception(vt_result['error'])
            
            vt_success = True
            source_used = 'VirusTotal'
            vt_data = vt_result
                 
        except Exception as e:
            logger.warning(f"VirusTotal fallo ({e}). Activando Google Safe Browsing (Fallback)...")
            vt_success = False

        # 2. Si falla VT, usamos Google Safe Browsing
        gsb_success = False
        if not vt_success:
            from services.google_safe_browsing_service import GoogleSafeBrowsingService
            
            try:
                gsb_service = GoogleSafeBrowsingService()
                gsb_result = gsb_service.check_url(url)
                
                if 'error' not in gsb_result:
                    gsb_success = True
                    source_used = gsb_result['source']
                    
                    # Mapeamos resultado GSB a variables comunes
                    # GSB no tiene "positives/total" numérico real, asi que simulamos
                    if not gsb_result['safe']:
                        positives = 1
                        total = 1
                        risk = gsb_result['risk_level'] # CRITICAL
                        message = gsb_result['message']
                        detail = gsb_result['detail']
                    else:
                        positives = 0
                        total = 1
                        risk = gsb_result['risk_level'] # LOW
                        message = gsb_result['message']
                        detail = gsb_result['detail']
            except Exception as e:
                logger.error(f"Fallo critico GSB: {e}")
                gsb_success = False

            if not gsb_success:
                 # Si ambos fallan
                 return Response({
                     'risk_level': 'UNKNOWN',
                     'message': 'Servicio no disponible',
                     'detail': 'No se pudo verificar la URL con ninguno de los motores (VirusTotal/Google).',
                     'positives': 0,
                     'total': 0
                 }, status=200)

        # 3. Procesar resultado de VirusTotal (si tuvo exito)
        if vt_success:
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

        # 4. Gemini (Explicacion Humana para CUALQUIER resultado)
        gemini_explicacion = ''
        gemini_recomendacion = ''
        try:
            gemini_service = GeminiService()
            # Pasamos positives/total unificados
            gemini_result = gemini_service.explain_threat(positives, total, 'url')
            if gemini_result:
                gemini_explicacion = gemini_result.get('explicacion', '')
                gemini_recomendacion = gemini_result.get('recomendacion', '')
        except Exception as e:
            logger.warning(f"Gemini no disponible: {e}")
        
        return Response({
            'risk_level': risk,
            'message': message,
            'detail': detail,
            'virustotal': vt_data,
            'source': source_used,
            'gemini_explicacion': gemini_explicacion,
            'gemini_recomendacion': gemini_recomendacion,
            'positives': positives,
            'total': total
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_stats(request):
    """
    Estadísticas para el Dashboard de Analista.
    Solo para analistas y admins.
    """
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role not in ['admin', 'analyst']:
            return Response({'error': 'No autorizado'}, status=403)

        total_incidents = Incident.objects.count()
        pending_incidents = Incident.objects.filter(status='pending').count()
        critical_incidents = Incident.objects.filter(risk_level='CRITICAL').count()
        
        # Estadísticas por tipo
        files_count = Incident.objects.filter(incident_type='file').count()
        urls_count = Incident.objects.filter(incident_type='url').count()
        
        return Response({
            'total': total_incidents,
            'pending': pending_incidents,
            'critical': critical_incidents,
            'by_type': {
                'files': files_count,
                'urls': urls_count
            }
        })
    except Exception as e:
        logger.error(f"Error en estadísticas: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_incident_status(request, incident_id):
    """
    Actualizar estado de incidente (Analistas).
    """
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role not in ['admin', 'analyst']:
            return Response({'error': 'No autorizado'}, status=403)
            
        incident = Incident.objects.get(id=incident_id)
        new_status = request.data.get('status')
        
        if new_status in ['pending', 'in_progress', 'resolved', 'closed']:
            incident.status = new_status
            incident.save()
            return Response({'message': 'Estado actualizado', 'status': new_status})
        else:
            return Response({'error': 'Estado inválido'}, status=400)
            
    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, incident_id):
    """
    Genera un reporte PDF del incidente.
    """
    try:
        incident = Incident.objects.get(id=incident_id)
        
        # Validar permisos (Solo el creador o analistas/admin pueden ver)
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role == 'employee' and incident.reported_by != request.user:
            return Response({'error': 'No autorizado'}, status=403)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_incidente_{incident.id}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        w, h = letter

        # Encabezado
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, h - 50, f"Reporte de Incidente de Seguridad #{incident.id}")
        
        p.setFont("Helvetica", 12)
        p.drawString(50, h - 80, f"Fecha: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        p.drawString(50, h - 100, f"Reportado por: {incident.reported_by.username}")
        p.drawString(50, h - 120, f"Estado Actual: {incident.status.upper()}")
        
        # Detalles
        p.line(50, h - 140, 550, h - 140)
        
        y = h - 170
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Detalles del Análisis:")
        y -= 20
        
        p.setFont("Helvetica", 10)
        p.drawString(50, y, f"Tipo: {incident.incident_type}")
        y -= 15
        p.drawString(50, y, f"Objetivo: {incident.url or incident.attached_file.name}")
        y -= 15
        p.drawString(50, y, f"Nivel de Riesgo: {incident.risk_level}")
        y -= 25
        
        # Resultados Técnicos
        if incident.virustotal_result:
            positives = incident.virustotal_result.get('positives', 0)
            total = incident.virustotal_result.get('total', 0)
            p.drawString(50, y, f"Motores Antivirus (VirusTotal/MetaDefender): {positives}/{total} detecciones")
            y -= 25

        # Análisis IA
        if incident.gemini_analysis:
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Análisis de Asistente IA (Explicación):")
            y -= 20
            p.setFont("Helvetica-Oblique", 10)
            
            # Simple text wrap logic (very basic)
            text = incident.gemini_analysis
            lines = []
            while len(text) > 90:
                split_at = text[:90].rfind(' ')
                if split_at == -1: split_at = 90
                lines.append(text[:split_at])
                text = text[split_at:].strip()
            lines.append(text)
            
            for line in lines:
                p.drawString(50, y, line)
                y -= 15

        # Footer
        p.setFont("Helvetica", 8)
        p.drawString(50, 30, "Reporte generado automáticamente por Sistema de Asistente de Ciberseguridad")
        
        p.showPage()
        p.save()
        return response
        
    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        return Response({'error': str(e)}, status=500)
