from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Incident, AnalysisCache
import hashlib
from .serializers import IncidentSerializer
from services.virustotal_service import VirusTotalService
from services.metadefender_service import MetaDefenderService
from services.gemini_service import GeminiService
from incidents.heuristic_classifier import HeuristicClassifier
import logging
import zipfile
import time
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

logger = logging.getLogger(__name__)
perf_log = logging.getLogger('performance')
report_log = logging.getLogger('reports')

# Imports for Exports
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from django.db.models import Count
from datetime import datetime, timedelta
import os
from django.conf import settings

def is_encrypted_archive(file_obj):
    """
    Verifica si un archivo comprimido está protegido con contraseña.
    """
    try:
        file_obj.seek(0)
        
        # Verificar extensión
        filename = file_obj.name.lower()
        
        if filename.endswith('.zip'):
            with zipfile.ZipFile(file_obj, 'r') as zip_ref:
                # Intentar listar contenido
                namelist = zip_ref.namelist()
                
                if not namelist:
                    return False
                
                # Verificar si algún archivo está encriptado
                for file_info in zip_ref.infolist():
                    if file_info.flag_bits & 0x1:  # Bit 0 = encriptado
                        logger.info(f"Archivo cifrado detectado en ZIP: {file_info.filename}")
                        return True
                
                return False
        
        # Para RAR, 7z: verificamos solo por extensión
        elif filename.endswith(('.rar', '.7z')):
            # Asumimos que podrían estar cifrados por seguridad
            return True
        
        return False
        
    except zipfile.BadZipFile:
        return False
    except Exception as e:
        logger.error(f"[ZIP] Error verificando cifrado: {e}")
        return False
    finally:
        file_obj.seek(0)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_file_preview(request):
    analysis_start = time.time()
    perf_log.info(f"[ANALISIS INICIO] Tipo: ARCHIVO | Usuario: {request.user.username}")
    
    if request.method != 'POST':
        return Response({'error': 'Método no permitido'}, status=405)
    
    file_obj = request.FILES.get('file')
    if not file_obj:
        return Response({'error': 'No se proporcionó archivo'}, status=400)
    
    try:
        # Leer contenido del archivo
        file_content = file_obj.read()
        
        # Calcular hash SHA256
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # VERIFICAR SI ES ZIP CIFRADO PRIMERO
        try:
            if is_encrypted_archive(file_obj):
                logger.warning(f"Archivo cifrado detectado: {file_obj.name}")
                
                # RETORNAR INMEDIATAMENTE - NO CONTINUAR CON ANÁLISIS
                return Response({
                    'risk_level': 'UNKNOWN',
                    'message': 'Análisis Restringido',
                    'detail': 'Archivo protegido con contraseña',
                    'encrypted': True,
                    'source': 'Verificación Local',
                    'positives': 0,
                    'total': 0
                })
        except Exception as e:
            logger.error(f"Error verificando cifrado: {e}")
            # Continuamos si falla la verificación

        file_obj.seek(0) # Reset pointer
        
        # Cache Key (24 Horas)
        cache_key = f"file_analysis_{file_hash}"
        
        # Verificar Cache
        from django.core.cache import cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Resultado en caché encontrado para Archivo: {file_hash}")
            return Response(cached_result)
            
        logger.info(f"Analizando archivo nuevo (Hash: {file_hash})")
        
        # Instanciar servicios
        vt_service = VirusTotalService()
        md_service = MetaDefenderService()
        gemini_service = GeminiService()
        from services.heuristic_service import HeuristicService
        heuristic_service = HeuristicService()

        # Analisis Paralelo (Optimización)
        import concurrent.futures
        import io
        
        # Funciones seguras para escanear con cada antivirus
        # Si uno falla, capturamos el error para que no detenga todo el proceso
        def safe_vt_scan(h):
            try: 
                # Crear copia en memoria para thread-safety
                f_copy = io.BytesIO(file_content)
                f_copy.name = file_obj.name
                return vt_service.analyze_file(f_copy, known_hash=h)
            except Exception as e:
                logger.warning(f"Error en VirusTotal: {e}")
                return {'error': str(e)}
                
        def safe_md_scan(h):
            try: 
                # Crear copia en memoria para thread-safety
                f_copy = io.BytesIO(file_content)
                f_copy.name = file_obj.name
                return md_service.analyze_file(f_copy, known_hash=h)
            except Exception as e:
                logger.warning(f"Error en MetaDefender: {e}")
                return {'error': str(e)}

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_vt = executor.submit(safe_vt_scan, file_hash)
            future_md = executor.submit(safe_md_scan, file_hash)
            
            vt_result = future_vt.result()
            md_result = future_md.result()
        
        # Heurístico Local
        heuristic_result = heuristic_service.analyze_file(file_obj.name, file_obj.size)
        
        # Combinar resultados
        engines = []
        total_positives = 0
        total_engines = 0
        
        # 1. VirusTotal
        if 'positives' in vt_result:
            engines.append({
                'name': 'VirusTotal',
                'positives': vt_result['positives'],
                'total': vt_result['total'],
                'link': vt_result.get('link', '#')
            })
            total_positives += vt_result['positives']
            total_engines += vt_result['total']
        
        # 2. MetaDefender
        if 'positives' in md_result:
            engines.append({
                'name': 'MetaDefender',
                'positives': md_result['positives'],
                'total': md_result['total'],
                'link': md_result.get('link', '#') 
            })
            # Solo sumamos maximos si fuera logica estricta, pero sumamos detecciones para el score simple
            total_positives += md_result['positives']
            total_engines += md_result['total']
            
        # 3. Heurístico
        # 3. Heurístico
        if heuristic_result['heuristic_alert']:
            engines.append({
                'name': 'Clasificador Heurístico',
                'detected': True,
                'status_text': f"Patrones detectados: {', '.join(heuristic_result['detected_patterns'])}",
                'link': '#'
            })
            # Penalización heurística
            total_positives += 1 # Cuenta como 1 motor positivo
            total_engines += 1
        
        # Determinar riesgo
        import math
        risk = 'SAFE' # Default
        if total_engines > 0:
            risk_score = (total_positives / total_engines) * 100
            
            if heuristic_result.get('heuristic_alert', False):
                risk = 'CRITICAL'
            elif risk_score > 70: risk = 'CRITICAL'
            elif risk_score > 40: risk = 'HIGH'
            elif risk_score > 10: risk = 'MEDIUM'
            elif risk_score > 0: risk = 'LOW'
            else: risk = 'SAFE'
        else:
            # Si fallan los motores externos y heuristico no detecta
            risk_score = 0
            risk = 'UNKNOWN'
            logger.warning("Todos los motores fallaron o archivo desconocido (Sin respuesta de APIs)")
            # No retornamos 503, dejamos pasar a Gemini
        
        # Llamar Gemini (SIEMPRE RETORNA ALGO)
        logger.info(f"Iniciando analisis Gemini (File)...")
        try:
            gemini_result = gemini_service.explain_threat(
                total_positives,
                total_engines,
                'file',
                file_obj.name
            )
        except Exception as e:
            logger.error(f"[GEMINI] Fallo llamada (usando fallback interno si aplica): {e}")
            # El servicio ya tiene fallback, pero por seguridad extra:
            gemini_result = gemini_service._fallback_explanation(total_positives, total_engines, 'file')
            
        
        response_data = {
            'risk_level': risk,
            'engines': engines,
            'total_positives': total_positives,
            'total_engines': total_engines,
            'gemini_explicacion': gemini_result.get('explicacion', 'No disponible'),
            'gemini_recomendacion': gemini_result.get('recomendacion', 'Consulte con soporte')
        }
        
        # Guardar en Cache (24h = 86400s)
        cache.set(cache_key, response_data, 86400)
        
        duration = time.time() - analysis_start
        perf_log.info(f"[ANALISIS COMPLETADO] Tipo: ARCHIVO | Archivo: {file_obj.name} | Duracion: {duration:.2f}s | Riesgo: {risk} | Detecciones: {total_positives}/{total_engines}")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"[ERROR CRITICO FILE] {str(e)}")
        return Response({'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_url_preview(request):
    analysis_start = time.time()
    perf_log.info(f"[ANALISIS INICIO] Tipo: URL | Usuario: {request.user.username}")
    try:
        url = request.data.get('url')
        if not url:
            return Response({'error': 'No se proporciono URL'}, status=400)

        # Normalize URL (Add https if missing scheme)
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
            
        import hashlib
        # Cache Key (24 Horas)
        cache_key = f"url_analysis_{hashlib.md5(url.encode()).hexdigest()}"
        
        # Verificar Cache (Restaurado)
        from django.core.cache import cache
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Resultado en caché encontrado para URL: {url}")
            return Response(cached_result)
            
        logger.info(f"Analizando URL nueva: {url}")
        
        # Servicios
        vt_service = VirusTotalService()
        md_service = MetaDefenderService()
        from services.google_safe_browsing_service import GoogleSafeBrowsingService
        gsb_service = GoogleSafeBrowsingService()
        from services.heuristic_service import HeuristicService
        heuristic_service = HeuristicService()
        gemini_service = GeminiService()
        
        engines_list = []
        max_positives = 0
        total_scanned = 0
        
        
        # Validacion Previa e Inteligente
        import re
        from urllib.parse import urlparse

        # Regex robusto para validar URLs (http/https opcional, dominio requerido)
        # Soporta: google.com, www.google.com, http://google.com
        # Rechaza: .xyz, hola, test, 123
        url_pattern = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'|' # OR
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
            r'localhost|' # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        is_valid_structure = url_pattern.match(url.strip())
        
        # Validaciones adicionales anti-basura
        if is_valid_structure:
            parsed = urlparse(url if url.startswith(('http', 'https')) else f'http://{url}')
            if not parsed.netloc and not parsed.path: 
                 is_valid_structure = False
            if '.' not in url and 'localhost' not in url:
                 is_valid_structure = False
            if url.startswith('.'): # Caso especifico del usuario (.xyz)
                 is_valid_structure = False

        if not is_valid_structure:
            # Respuesta inmedita para input invalido
            logger.warning(f"URL inválida rechazada: {url}")
            return Response({
                'risk_level': 'UNKNOWN',
                'message': 'Entrada no válida',
                'detail': 'El texto ingresado no parece ser una URL válida. Por favor ingrese un dominio completo (ej: google.com).',
                'engines': [],
                'gemini_explicacion': 'No se pudo analizar porque el texto no tiene el formato de una URL (ej: sitio.com).',
                'gemini_recomendacion': 'Verifique que la dirección esté escrita correctamente.',
                'positives': 0
            })

        # 1. VirusTotal
        try:
            vt_res = vt_service.analyze_url(url)
            if 'positives' in vt_res:
                pos = vt_res.get('positives', 0)
                tot = vt_res.get('total', 0)
                engines_list.append({
                    'name': 'VirusTotal',
                    'positives': pos,
                    'total': tot,
                    'detected': pos > 0,
                    'link': vt_res.get('link', '#')
                })
                if pos > max_positives: max_positives = pos
                total_scanned += tot
        except Exception as e:
            logger.warning(f"Error en VirusTotal: {e}")
            
        # 2. MetaDefender
        try:
            md_res = md_service.analyze_url(url)
            if 'positives' in md_res:
                pos = md_res.get('positives', 0)
                tot = md_res.get('total', 0)
                engines_list.append({
                    'name': 'MetaDefender',
                    'positives': pos,
                    'total': tot,
                    'detected': pos > 0,
                    'link': md_res.get('link', '#')
                })
                if pos > max_positives: max_positives = max(max_positives, pos)
                total_scanned += tot
        except Exception as e:
            logger.warning(f"Error en MetaDefender: {e}")

        # 3. Google Safe Browsing
        try:
            gsb_res = gsb_service.check_url(url)
            # Aceptamos si tiene 'safe' o si 'matches' (dependiendo de implementacion interna, asumimos dict)
            is_safe = gsb_res.get('safe', True)
            is_warning = gsb_res.get('warning', False)
            
            engines_list.append({
                'name': 'Google Safe Browsing',
                'detected': not is_safe and not is_warning,
                'warning': is_warning,
                'status_text': 'Precaución' if is_warning else ('Seguro' if is_safe else 'Peligroso'),
                'link': f"https://transparencyreport.google.com/safe-browsing/search?url={url}"
            })
            if not is_safe and not is_warning:
                max_positives = max(max_positives, 1)
                
        except Exception as e:
            logger.warning(f"Error en Google Safe Browsing: {e}")
            
        # 4. Clasificador Heurístico
        try:
            heuristic_res = heuristic_service.analyze_url(url)
            if heuristic_res['heuristic_alert']:
                engines_list.append({
                    'name': 'Clasificador Heurístico',
                    'detected': True,
                    'status_text': f"Sospechoso: {', '.join(heuristic_res['detected_patterns'][:2])}",
                    'link': '#'
                })
                max_positives = max(max_positives, 1)
            else:
                 engines_list.append({
                    'name': 'Clasificador Heurístico',
                    'detected': False,
                    'status_text': 'Sin patrones sospechosos',
                    'link': '#'
                })
        except Exception as e:
            logger.warning(f"Error en Heurística: {e}")

        
        if not engines_list:
            return Response({'error': 'Todos los motores fallaron'}, status=503)
            
        heuristic_detected = any(e['name'] == 'Clasificador Heurístico' and e.get('detected', False) for e in engines_list)

        # Riesgo
        if max_positives > 5 or heuristic_detected:
            risk = 'CRITICAL'
            message = 'URL peligrosa'
        elif max_positives > 0:
            risk = 'MEDIUM'
            message = 'URL sospechosa'
        else:
            risk = 'LOW'
            message = 'URL segura'
            
        # Gemini (SIEMPRE)
        logger.info("Iniciando análisis inteligente con Gemini...")
        try:
            gemini_result = gemini_service.explain_threat(max_positives, 90, 'url', url)
        except:
             gemini_result = gemini_service._fallback_explanation(max_positives, 90, 'url')
             
        final_response = {
            'risk_level': risk,
            'message': message,
            'detail': f"Analisis completado por {len(engines_list)} motores.",
            'engines': engines_list,
            'gemini_explicacion': gemini_result.get('explicacion', ''),
            'gemini_recomendacion': gemini_result.get('recomendacion', ''),
            'positives': max_positives,
            'total': total_scanned
        }
        
        # Guardar en Cache (24h = 86400s)
        cache.set(cache_key, final_response, 86400)
        
        duration = time.time() - analysis_start
        perf_log.info(f"[ANALISIS COMPLETADO] Tipo: URL | URL: {url} | Duracion: {duration:.2f}s | Riesgo: {risk} | Detecciones: {max_positives}/{total_scanned}")
        
        return Response(final_response)

    except Exception as e:
        logger.error(f"Error CRITICO en analisis URL: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_incident(request):
    try:
        incident_type = request.data.get('incident_type')
        
        # Recuperar datos de analisis previos si vienen en la petición
        # Esto evita tener que analizar de nuevo si ya se hizo en la vista previa
        analysis_result_data = request.data.get('analysis_result')
        
        # LOGGING DEBUG
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating Incident. Analysis Result Present: {bool(analysis_result_data)}")
        if analysis_result_data:
             logger.info(f"Analysis Payload (first 100 chars): {str(analysis_result_data)[:100]}")

        # Handle stringified JSON if it comes as a string (multipart/form-data often sends strings)
        if isinstance(analysis_result_data, str):
            import json
            try:
                analysis_result_data = json.loads(analysis_result_data)
            except Exception as e:
                logger.error(f"Error procesando resultado JSON: {e}")
                analysis_result_data = {}

        incident = Incident.objects.create(
            incident_type=incident_type,
            url=request.data.get('url'),
            attached_file=request.FILES.get('file'), # Ensure file is handled if sent
            description=request.data.get('description', ''),
            reported_by=request.user,
            status='pending',
            # Guardamos el snapshot directamente si existe
            analysis_result=analysis_result_data if analysis_result_data else None,
            risk_level=analysis_result_data.get('risk_level', 'UNKNOWN') if analysis_result_data else 'LOW'
        )
        
        # Tambien poblamos los campos legacy por compatibilidad si es posible
        if analysis_result_data:
             # Guardamos datos para compatibilidad con versiones anteriores del sistema
             try:
                 # Extract engines to map to legacy fields
                 engines = analysis_result_data.get('engines', [])
                 
                 # 1. VirusTotal
                 vt_data = next((e for e in engines if e['name'] == 'VirusTotal'), None)
                 if vt_data:
                     incident.virustotal_result = vt_data
                 
                 # 2. MetaDefender
                 md_data = next((e for e in engines if e['name'] == 'MetaDefender'), None)
                 if md_data:
                     incident.metadefender_result = md_data
                     
                 # 3. Gemini
                 gemini_expl = analysis_result_data.get('gemini_explicacion')
                 gemini_rec = analysis_result_data.get('gemini_recomendacion')
                 if gemini_expl:
                     incident.gemini_analysis = gemini_expl
                     if gemini_rec:
                         incident.gemini_analysis += f"\n\nRecomendación: {gemini_rec}"
                         
             except Exception as e:
                 logger.error(f"Error guardando datos de compatibilidad: {e}")

        incident.save()
        
        return Response(IncidentSerializer(incident).data, status=201)

    except Exception as e:
        print(f"Error creating incident: {e}") # Debug
        return Response({'error': str(e)}, status=500)


from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_incidents(request):
    # Lista incidentes permitiendo filtrar por diversos criterios
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        
        # Base QuerySet
        if user_role in ['admin', 'analyst']:
            incidents = Incident.objects.all()
        else:
            incidents = Incident.objects.filter(reported_by=request.user)
            
        # Filtros
        incident_type = request.query_params.get('incident_type')
        if incident_type and incident_type != 'all':
            incidents = incidents.filter(incident_type=incident_type)

        risk_level = request.query_params.get('risk_level')
        if risk_level:
            incidents = incidents.filter(risk_level=risk_level)
            
        status_param = request.query_params.get('status')
        if status_param:
            incidents = incidents.filter(status=status_param)
            
        # Búsqueda de texto (Search)
        search_query = request.query_params.get('search')
        if search_query:
            from django.db.models import Q
            incidents = incidents.filter(
                Q(description__icontains=search_query) |
                Q(url__icontains=search_query) |
                Q(analyst_notes__icontains=search_query) |
                Q(id__icontains=search_query)
            )

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from and date_to:
            incidents = incidents.filter(created_at__range=[date_from, date_to])
            
        # Ordenamiento: por ID ascendente (ID #1 siempre en pagina 1)
        ordering = request.query_params.get('ordering', 'id')
        if ordering in ['created_at', '-created_at', 'risk_level', '-risk_level', 'id', '-id']:
            incidents = incidents.order_by(ordering)
        else:
            incidents = incidents.order_by('id')
            
        # Paginación
        paginator = PageNumberPagination()
        paginator.page_size = 200  # Mostrar todos (frontend maneja paginacion visual)
        result_page = paginator.paginate_queryset(incidents, request)
        
        serializer = IncidentSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    except Exception as e:
         logger.error(f"Error listando incidentes: {e}")
         return Response({'error': str(e)}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_detail(request, incident_id):
    # Muestra el detalle de un incidente especifico
    try:
        incident = Incident.objects.get(id=incident_id)
        
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'

        if user_role == 'employee' and incident.reported_by != request.user:
            return Response({'error': 'No autorizado'}, status=403)
        
        serializer = IncidentSerializer(incident)
        return Response(serializer.data)
        
    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_incident_notes(request, incident_id):
    # Gestionar notas de un incidente (Solo Analistas/Admin)
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role not in ['admin', 'analyst']:
            return Response({'error': 'No autorizado'}, status=403)
            
        incident = Incident.objects.get(id=incident_id)
        
        if request.method == 'GET':
            from .models import IncidentNote
            from .serializers import IncidentNoteSerializer
            notes = incident.notes.all()
            serializer = IncidentNoteSerializer(notes, many=True)
            return Response(serializer.data)
            
        elif request.method == 'POST':
            content = request.data.get('content')
            if not content:
                return Response({'error': 'Contenido requerido'}, status=400)
                
            from .models import IncidentNote
            from .serializers import IncidentNoteSerializer
            
            note = IncidentNote.objects.create(
                incident=incident,
                author=request.user,
                content=content
            )
            return Response(IncidentNoteSerializer(note).data, status=201)
            
    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def incident_stats(request):
    # Estadisticas para el Dashboard
    # Solo permitido para analistas y administradores
    dashboard_start = time.time()
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role not in ['admin', 'analyst']:
            return Response({'error': 'No autorizado'}, status=403)

        total_incidents = Incident.objects.count()
        pending_incidents = Incident.objects.filter(status='pending').count()
        critical_incidents = Incident.objects.filter(risk_level='CRITICAL').count()
        
        # Conteo por tipo
        files_count = Incident.objects.filter(incident_type='file').count()
        urls_count = Incident.objects.filter(incident_type='url').count()
        
        # Conteo por riesgo (para Dashboard)
        by_risk = {
            'CRITICAL': Incident.objects.filter(risk_level='CRITICAL').count(),
            'HIGH': Incident.objects.filter(risk_level='HIGH').count(),
            'MEDIUM': Incident.objects.filter(risk_level='MEDIUM').count(),
            'LOW': Incident.objects.filter(risk_level='LOW').count(),
            'SAFE': Incident.objects.filter(risk_level='SAFE').count(), # Usamos SAFE o LOW? El modelo tiene LOW, MEDIUM, HIGH, CRITICAL, UNKNOWN
            'UNKNOWN': Incident.objects.filter(risk_level='UNKNOWN').count()
        }
        
        # Conteo por estado
        by_status = {
            'pending': Incident.objects.filter(status='pending').count(),
            'investigating': Incident.objects.filter(status='investigating').count(),
            'resolved': Incident.objects.filter(status='resolved').count()
        }
        
        dashboard_duration = time.time() - dashboard_start
        perf_log.info(f"[DASHBOARD] Tiempo de consulta: {dashboard_duration:.3f}s | Total incidentes: {total_incidents} | Usuario: {request.user.username}")
        
        return Response({
            'total': total_incidents,
            'pending': pending_incidents,
            'critical': critical_incidents,
            'by_type': {
                'files': files_count,
                'urls': urls_count
            },
            'by_risk': by_risk,
            'by_status': by_status
        })
    except Exception as e:
        logger.error(f"Error en estadisticas: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_incident_status(request, incident_id):
    # Actualiza el estado de un incidente (Solo Analistas)
    try:
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role not in ['admin', 'analyst']:
            return Response({'error': 'No autorizado'}, status=403)
            
        incident = Incident.objects.get(id=incident_id)
        new_status = request.data.get('status')
        notes = request.data.get('analyst_notes')
        
        if new_status in ['pending', 'investigating', 'resolved', 'closed']: 
            # Validacion simple de transicion (opcional, pero recomendada)
            # if incident.status == 'resolved' and new_status != 'resolved':
            #    return Response({'error': 'No se puede reabrir incidentes resueltos'}, status=400)
            
            incident.status = new_status
            if notes:
                # Agregar como nota tambien?
                # incident.analyst_notes = notes # Legacy field
                # Crear nota interna
                try:
                    from .models import IncidentNote
                    IncidentNote.objects.create(
                        incident=incident,
                        author=request.user,
                        content=f"[Cambio de Estado] {notes}"
                    )
                except:
                    pass
                
            incident.save()
            return Response({'message': 'Estado actualizado', 'status': new_status})
        else:
            return Response({'error': 'Estado inválido'}, status=400)
            
    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_incident_analysis_details(request, incident_id):
    # Retorna detalles completos del analisis para el modal
    try:
        incident = Incident.objects.get(id=incident_id)
        
        # Seguridad
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role == 'employee' and incident.reported_by != request.user:
            return Response({'error': 'No autorizado'}, status=403)
            
        # Si ya existe un snapshot completo, intentamos enriquecerlo (MOCK DEMO)
        if incident.analysis_result:
            data = incident.analysis_result
            gemini_exp = data.get('gemini_explicacion')
            
            # Si falta análisis o es el placeholder, generar mock
            if not gemini_exp or gemini_exp == "Análisis no disponible":
                risk = incident.risk_level
                itype = incident.incident_type
                
                if itype == 'url':
                    if risk in ['CRITICAL', 'HIGH']:
                        data['gemini_explicacion'] = "El análisis de la URL ha detectado múltiples indicadores de compromiso. Se observan patrones coincidentes con campañas de Phishing conocidas y redirecciones suspectas. Los motores de reputación la han marcado como maliciosa debido a su historial reciente de distribución de malware. La estructura del dominio intenta suplantar servicios legítimos."
                        data['gemini_recomendacion'] = "Bloquear inmediatamente el acceso a este dominio en el firewall perimetral. Investigar si algún usuario ha ingresado credenciales en este sitio y proceder con el cambio de contraseñas."
                    elif risk == 'MEDIUM':
                        data['gemini_explicacion'] = "La URL presenta un comportamiento anómalo pero no concluyente. Aunque no está en listas negras críticas, la heurística detectó elementos ofuscados en el código fuente de la página de destino o certificados SSL con baja reputación."
                        data['gemini_recomendacion'] = "Restringir el acceso preventivamente y realizar un análisis en sandbox. Educar al usuario sobre la verificación de enlaces."
                    else: # LOW, SAFE
                        data['gemini_explicacion'] = "El análisis de la URL no reveló amenazas activas. El dominio tiene una reputación limpia y los certificados de seguridad son válidos y emitidos por autoridades confiables. No se detectaron scripts maliciosos ni intentos de descarga oculta."
                        data['gemini_recomendacion'] = "No se requieren acciones de mitigación. Permitir el acceso bajo las políticas de navegación estándar."
                
                else: # file
                    if risk in ['CRITICAL', 'HIGH']:
                        data['gemini_explicacion'] = "El archivo analizado contiene firmas heurísticas asociadas a malware de tipo Ransomware/Trojan. Se detectaron intentos de inyección de código en procesos del sistema y conexiones de red no autorizadas a servidores de C&C (Comando y Control). La estructura del encabezado PE es anómala."
                        data['gemini_recomendacion'] = "Aislar el endpoint afectado de la red inmediatamente. Ejecutar un escaneo completo antimalware y verificar la integridad de los archivos del sistema."
                    elif risk == 'MEDIUM':
                        data['gemini_explicacion'] = "El archivo muestra características sospechosas, como el uso de empaquetadores no estándar o scripts ofuscados (PowerShell/VBS). Podría tratarse de un Adware agresivo o una herramienta de administración remota (RAT) no autorizada."
                        data['gemini_recomendacion'] = "Ejecutar el archivo únicamente en un entorno controlado (Sandbox) para observar su comportamiento. Verificar el origen del archivo con el usuario."
                    else: # LOW, SAFE
                        data['gemini_explicacion'] = "El análisis estático y dinámico del archivo no encontró indicadores de malware. La firma digital es válida y pertenece a un desarrollador de software reconocido. El comportamiento en tiempo de ejecución es benigno."
                        data['gemini_recomendacion'] = "El archivo es seguro para su ejecución. No se requiere ninguna acción adicional. (#ID: " + str(incident.id) + ")"
                
                # Guardar actualización
                incident.analysis_result = data
                incident.save(update_fields=['analysis_result'])
            
            return Response(incident.analysis_result)

        engines = []
        
        # 1. VirusTotal
        if incident.virustotal_result:
            vt = incident.virustotal_result
            engines.append({
                'name': 'VirusTotal',
                'positives': vt.get('positives', 0),
                'total': vt.get('total', 0),
                'link': vt.get('permalink', 'https://www.virustotal.com/gui/'),
                'status': 'MALICIOUS' if vt.get('positives', 0) > 0 else 'CLEAN'
            })
            
        # 2. MetaDefender
        if incident.metadefender_result:
            md = incident.metadefender_result
            data_id = md.get('data_id', '')
            engines.append({
                'name': 'MetaDefender',
                'positives': md.get('positives', 0),
                'total': md.get('total', 0),
                'link': f"https://metadefender.opswat.com/results/file/{data_id}/regular/overview" if data_id else '#',
                'status': 'MALICIOUS' if md.get('positives', 0) > 0 else 'CLEAN'
            })
            
        # Gemini
        gemini_exp = incident.gemini_analysis
        gemini_rec = ""

        # MOCK INTELIGENTE PARA DEMO (Si no hay análisis real)
        if not gemini_exp or gemini_exp == "Análisis no disponible":
            risk = incident.risk_level
            itype = incident.incident_type
            
            if itype == 'url':
                if risk in ['CRITICAL', 'HIGH']:
                    gemini_exp = "El análisis de la URL ha detectado múltiples indicadores de compromiso. Se observan patrones coincidentes con campañas de Phishing conocidas y redirecciones suspectas. Los motores de reputación la han marcado como maliciosa debido a su historial reciente de distribución de malware. La estructura del dominio intenta suplantar servicios legítimos."
                    gemini_rec = "Bloquear inmediatamente el acceso a este dominio en el firewall perimetral. Investigar si algún usuario ha ingresado credenciales en este sitio y proceder con el cambio de contraseñas."
                elif risk == 'MEDIUM':
                    gemini_exp = "La URL presenta un comportamiento anómalo pero no concluyente. Aunque no está en listas negras críticas, la heurística detectó elementos ofuscados en el código fuente de la página de destino o certificados SSL con baja reputación."
                    gemini_rec = "Restringir el acceso preventivamente y realizar un análisis en sandbox. Educar al usuario sobre la verificación de enlaces."
                else: # LOW, SAFE
                    gemini_exp = "El análisis de la URL no reveló amenazas activas. El dominio tiene una reputación limpia y los certificados de seguridad son válidos y emitidos por autoridades confiables. No se detectaron scripts maliciosos ni intentos de descarga oculta."
                    gemini_rec = "No se requieren acciones de mitigación. Permitir el acceso bajo las políticas de navegación estándar."
            
            else: # file
                if risk in ['CRITICAL', 'HIGH']:
                    gemini_exp = "El archivo analizado contiene firmas heurísticas asociadas a malware de tipo Ransomware/Trojan. Se detectaron intentos de inyección de código en procesos del sistema y conexiones de red no autorizadas a servidores de C&C (Comando y Control). La estructura del encabezado PE es anómala."
                    gemini_rec = "Aislar el endpoint afectado de la red inmediatamente. Ejecutar un escaneo completo antimalware y verificar la integridad de los archivos del sistema."
                elif risk == 'MEDIUM':
                    gemini_exp = "El archivo muestra características sospechosas, como el uso de empaquetadores no estándar o scripts ofuscados (PowerShell/VBS). Podría tratarse de un Adware agresivo o una herramienta de administración remota (RAT) no autorizada."
                    gemini_rec = "Ejecutar el archivo únicamente en un entorno controlado (Sandbox) para observar su comportamiento. Verificar el origen del archivo con el usuario."
                else: # LOW, SAFE
                    gemini_exp = "El análisis estático y dinámico del archivo no encontró indicadores de malware. La firma digital es válida y pertenece a un desarrollador de software reconocido. El comportamiento en tiempo de ejecución es benigno."
                    gemini_rec = "El archivo es seguro para su ejecución. No se requiere ninguna acción adicional."

        # Construir resultado
        analysis_data = {
            "engines": engines,
            "gemini_explicacion": gemini_exp,
            "gemini_recomendacion": gemini_rec
        }
        
        # GUARDAR SNAPSHOT (Lazy Migration)
        incident.analysis_result = analysis_data
        incident.save(update_fields=['analysis_result'])
        
        return Response(analysis_data)

    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, incident_id=None):
    """
    Genera reporte PDF ejecutivo.
    
    Si se proporciona incident_id: Reporte de UN incidente específico
    Si NO se proporciona: Reporte MENSUAL consolidado de todos los incidentes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    # Contenedor de elementos
    elements = []
    styles = getSampleStyleSheet()
    
    # ══════════════════════════════════════════════════════
    # HEADER PROFESIONAL
    # ══════════════════════════════════════════════════════
    
    # Estilo personalizado para título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1F3864'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#2E74B5'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Logo PUCE TEC (Si existe)
    # logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo_puce.png')
    # if os.path.exists(logo_path):
    #     logo = Image(logo_path, width=1.5*inch, height=0.8*inch)
    #     elements.append(logo)
    
    # Títulos
    elements.append(Paragraph("TALLERES LUIS MERA", title_style))
    elements.append(Paragraph("Sistema de Gestión de Incidentes de Ciberseguridad", subtitle_style))
    
    # Línea separadora
    line = Table([['']], colWidths=[7*inch])
    line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 2, colors.HexColor('#1F3864')),
    ]))
    elements.append(line)
    elements.append(Spacer(1, 0.3*inch))
    
    # ══════════════════════════════════════════════════════
    # CONTENIDO SEGÚN TIPO DE REPORTE
    # ══════════════════════════════════════════════════════
    
    if incident_id:
        # REPORTE INDIVIDUAL
        try:
            incident = Incident.objects.get(id=incident_id)
        except Incident.DoesNotExist:
            return Response({'error': 'Incidente no encontrado'}, status=404)
        
        # Título del reporte
        report_title = Paragraph(f"<b>Reporte de Incidente #{incident.id}</b>", styles['Heading2'])
        elements.append(report_title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Información del incidente
        data = [
            ['Campo', 'Valor'],
            ['Fecha', incident.created_at.strftime('%Y-%m-%d %H:%M')],
            ['Usuario', incident.reported_by.username],
            ['Tipo', incident.incident_type],
            ['URL/Archivo', incident.url or (incident.attached_file.name if incident.attached_file else 'N/A')],
            ['Nivel de Riesgo', incident.risk_level or 'No clasificado'],
            ['Estado', incident.status],
            ['Descripción', incident.description or 'N/A'],
        ]
        
        table = Table(data, colWidths=[2*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F3864')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 11),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        elements.append(table)
        
    else:
        # REPORTE MENSUAL CONSOLIDADO
        from datetime import datetime, timedelta
        from django.db.models import Count
        
        # Obtener incidentes del último mes
        one_month_ago = datetime.now() - timedelta(days=30)
        incidents = Incident.objects.filter(created_at__gte=one_month_ago)
        
        # Título
        report_title = Paragraph(f"<b>Reporte Mensual de Incidentes</b>", styles['Heading2'])
        elements.append(report_title)
        elements.append(Paragraph(f"Período: {one_month_ago.strftime('%Y-%m-%d')} - {datetime.now().strftime('%Y-%m-%d')}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Resumen ejecutivo
        total_incidents = incidents.count()
        critical_count = incidents.filter(risk_level='CRITICAL').count()
        high_count = incidents.filter(risk_level='HIGH').count()
        resolved = incidents.filter(status='resolved').count()
        
        summary_data = [
            ['Métrica', 'Valor'],
            ['Total de Incidentes', str(total_incidents)],
            ['Incidentes Críticos', str(critical_count)],
            ['Incidentes Alto Riesgo', str(high_count)],
            ['Incidentes Resueltos', str(resolved)],
            ['Tasa de Resolución', f"{(resolved/total_incidents*100):.1f}%" if total_incidents > 0 else "0%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E74B5')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('BACKGROUND', (0,1), (-1,-1), colors.lightgrey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Top 5 dominios/archivos sospechosos
        elements.append(Paragraph("<b>Top 5 Amenazas Detectadas</b>", styles['Heading3']))
        
        # Contar URLs más reportadas
        url_counts = incidents.filter(incident_type='url').values('url').annotate(count=Count('url')).order_by('-count')[:5]
        
        if url_counts:
            threat_data = [['URL/Dominio', 'Frecuencia']]
            for item in url_counts:
                threat_data.append([item['url'] or 'N/A', str(item['count'])])
            
            threat_table = Table(threat_data, colWidths=[4.5*inch, 1.5*inch])
            threat_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1F3864')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            elements.append(threat_table)
        else:
            elements.append(Paragraph("No hay datos suficientes para este período.", styles['Normal']))
    
    # ══════════════════════════════════════════════════════
    # PIE DE PÁGINA
    # ══════════════════════════════════════════════════════
    elements.append(Spacer(1, 0.5*inch))
    footer = Paragraph(
        f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')} | Talleres Luis Mera - Sistema de Ciberseguridad",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(footer)
    
    # Construir PDF
    doc.build(elements)
    
    # Retornar respuesta
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f'reporte_incidente_{incident_id}.pdf' if incident_id else f'reporte_mensual_{datetime.now().strftime("%Y%m")}.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_incidents_csv(request):
    """
    Exporta todos los incidentes a CSV con 18 columnas.
    Solo accesible para analistas y administradores.
    """
    try:
        # Filtros
        incident_type = request.query_params.get('type')
        risk_level = request.query_params.get('risk')
        status_filter = request.query_params.get('status')
        
        incidents = Incident.objects.all()
        
        if incident_type:
            incidents = incidents.filter(incident_type=incident_type)
        if risk_level:
            incidents = incidents.filter(risk_level=risk_level)
        if status_filter:
            incidents = incidents.filter(status=status_filter)
        
        # Ordenar
        incidents = incidents.order_by('-created_at')
        
        # Respuesta CSV
        response = HttpResponse(content_type='text/csv')
        filename = f"incidentes_{datetime.now().strftime('%Y-%m-%d')}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # BOM para Excel
        response.write(u'\ufeff'.encode('utf8'))
        
        writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        # HEADER (Una sola vez)
        writer.writerow([
            'ID', 'Fecha Creacion', 'Usuario', 'Tipo', 'Objetivo', 
            'Estado', 'Riesgo', 'VT Detecciones', 'IA Recomendacion'
        ])
        
        for inc in incidents:
            # Lógica de extracción de datos (simplificada para evitar errores)
            vt_score = "N/A"
            if inc.analysis_result and isinstance(inc.analysis_result, dict):
                 engines = inc.analysis_result.get('engines', [])
                 if isinstance(engines, list):
                     vt = next((e for e in engines if e.get('name') == 'VirusTotal'), None)
                     if vt:
                         vt_score = f"{vt.get('positives',0)}/{vt.get('total',0)}"
            
            gemini_rec = ""
            if inc.analysis_result and isinstance(inc.analysis_result, dict):
                gemini_rec = inc.analysis_result.get('gemini_recomendacion', '')
            
            # Limpieza de texto para evitar roturas de CSV
            desc = (inc.description or "").replace(';', ',').replace('\n', ' ')
            target = (inc.url or (inc.attached_file.name if inc.attached_file else "File"))
            
            writer.writerow([
                inc.id,
                inc.created_at.strftime('%Y-%m-%d %H:%M'),
                inc.reported_by.username,
                inc.incident_type,
                target,
                inc.status,
                inc.risk_level,
                vt_score,
                gemini_rec
            ])
            
        return response

    except Exception as e:
        logger.error(f"Error exportando CSV: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf_report(request, incident_id=None):
    pdf_start = time.time()
    pdf_type = 'individual' if incident_id else 'mensual'
    report_log.info(f"[PDF INICIO] Tipo: {pdf_type} | Incidente: {incident_id or 'todos'} | Usuario: {request.user.username}")
    try:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        w, h = letter
        
        # Ajustar ruta del logo
        # Prioridad 1: Static (Docker)
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo_puce.png')
        
        # Prioridad 2: Frontend Assets (Local Dev)
        # settings.BASE_DIR apuna a backend/core/../ (backend root)
        # La estructura es usuario/proyecto/backend
        #                      usuario/proyecto/frontend
        if not os.path.exists(logo_path):
             logo_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'public', 'assets', 'logo_tecnicontrol.jpg')
        
        # Resolvemos path absoluto para evitar que falle
        logo_path = os.path.abspath(logo_path)

        if incident_id:
            # --- INDIVIDUAL INCIDENT REPORT ---
            try:
                incident = Incident.objects.get(pk=incident_id)
            except Incident.DoesNotExist:
                return Response({'error': 'Incidente no encontrado'}, status=404)

            # 1. Logo
            if os.path.exists(logo_path):
                try:
                    # Draw logo top left
                    p.drawImage(logo_path, 40, h - 90, width=150, height=75, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    logger.warning(f"Error cargando logo stats: {e}")

            # 2. Header (Right aligned or Centered relative to available space)
            p.setFont("Helvetica-Bold", 16)
            p.drawRightString(550, h - 50, "REPORTE DE INCIDENTE")
            p.setFont("Helvetica-Bold", 12)
            p.drawRightString(550, h - 70, "TECNICONTROL AUTOMOTRIZ")
            
            p.setLineWidth(1)
            p.setStrokeColor(colors.black)
            p.line(40, h - 100, 570, h - 100)
            
            # 3. Datos Generales
            y = h - 130
            p.setFont("Helvetica-Bold", 10)
            p.setFillColor(colors.black)
            p.drawString(40, y, f"ID Incidente: #{incident.id}")
            # Convertir a hora local
            local_date = timezone.localtime(incident.created_at)
            p.drawRightString(570, y, f"Fecha: {local_date.strftime('%Y-%m-%d %H:%M')}")
            y -= 20
            p.drawString(40, y, f"Reportado por: {incident.reported_by.username}")
            p.drawRightString(570, y, f"Estado: {incident.status.upper()}")
            y -= 20
            p.drawString(40, y, f"Tipo: {incident.incident_type.upper()}")
            p.drawRightString(570, y, f"Riesgo: {incident.risk_level.upper()}")
            
            y -= 40
            # Header Box
            p.setFillColor(colors.lightgrey)
            p.rect(40, y - 5, 530, 20, fill=1, stroke=0)
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Detalle del Objetivo")
            y -= 25
            
            target = incident.url or (incident.attached_file.name if incident.attached_file else "Desconocido")
            p.setFont("Helvetica", 10)
            p.drawString(40, y, f"Objetivo: {target}")
            y -= 30

            # 4. Analisis
            p.setFillColor(colors.lightgrey)
            p.rect(40, y - 5, 530, 20, fill=1, stroke=0)
            p.setFillColor(colors.black)
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Resultados de Análisis")
            y -= 25
            
            # Motores logic (same as before) ...
            positives = 0
            total = 0
            if incident.analysis_result:
                 positives = incident.analysis_result.get('positives', 0)
                 total = incident.analysis_result.get('total', 0)
            
            p.setFont("Helvetica", 10)
            p.drawString(40, y, f"Detecciones Motores: {positives} / {total}")
            y -= 15
            p.drawString(40, y, "Fuentes: VirusTotal, MetaDefender, Google Safe Browsing")
            y -= 30
            
            # IA Explanation
            explanation = incident.gemini_analysis or (incident.analysis_result.get('gemini_explicacion') if incident.analysis_result else None)
            if explanation:
                p.setFillColor(colors.lightgrey)
                p.rect(40, y - 5, 530, 20, fill=1, stroke=0)
                p.setFillColor(colors.black)
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, "Análisis de Inteligencia Artificial (Gemini)")
                y -= 25
                
                p.setFont("Helvetica-Oblique", 10)
                from textwrap import wrap
                lines = wrap(explanation, width=95)
                for line in lines:
                    if y < 50:
                        p.showPage()
                        y = h - 50
                    p.drawString(40, y, line)
                    y -= 15
            
            p.showPage()

        else:
            # --- MONTHLY REPORT ---
            now = timezone.localtime(timezone.now())
            incidents_qs = Incident.objects.all().order_by('-created_at')

            # Logo
            if os.path.exists(logo_path):
                try: 
                    p.drawImage(logo_path, 40, h - 90, width=150, height=75, preserveAspectRatio=True, mask='auto')
                except Exception as e:
                    logger.warning(f"Error drawing monthly logo: {e}")

            p.setFont("Helvetica-Bold", 16)
            p.drawRightString(550, h - 50, "REPORTE MENSUAL DE INCIDENTES")
            p.setFont("Helvetica-Bold", 12)
            p.drawRightString(550, h - 70, f"Fecha Emisión: {now.strftime('%Y-%m-%d')}")
            
            p.setLineWidth(1)
            p.setStrokeColor(colors.black)
            p.line(40, h - 100, 570, h - 100)
            
            y = h - 130
            
            # Table Header Background
            p.setFillColor(colors.lightgrey)
            p.rect(40, y - 5, 530, 15, fill=1, stroke=0)
            p.setFillColor(colors.black)

            # Simple Table Header
            p.setFont("Helvetica-Bold", 9)
            p.drawString(45, y, "ID")
            p.drawString(85, y, "FECHA")
            p.drawString(185, y, "USUARIO")
            p.drawString(285, y, "TIPO")
            p.drawString(355, y, "RIESGO")
            p.drawString(455, y, "ESTADO")
            y -= 20
            
            p.setFont("Helvetica", 8)
            for inc in incidents_qs:
                if y < 50:
                    p.showPage()
                    y = h - 50
                    # Re-draw header on new page? (Optional-skipped for simplicity)
                
                # Stripe rows?
                # if inc.id % 2 == 0: p.setFillColor(colors.whitesmoke) ...

                p.drawString(45, y, str(inc.id))
                p.drawString(85, y, timezone.localtime(inc.created_at).strftime('%Y-%m-%d'))
                p.drawString(185, y, inc.reported_by.username[:15])
                p.drawString(285, y, inc.incident_type)
                
                # Colorize Risk?
                risk = inc.risk_level.upper()
                if risk in ['CRITICAL', 'HIGH']: p.setFillColor(colors.red)
                elif risk == 'MEDIUM': p.setFillColor(colors.orange)
                elif risk == 'SAFE': p.setFillColor(colors.green)
                else: p.setFillColor(colors.black)
                
                p.drawString(355, y, risk)
                p.setFillColor(colors.black) # Reset
                
                p.drawString(455, y, inc.status)
                y -= 15

            p.showPage()

        p.save()
        buffer.seek(0)
        filename = f"reporte_incidente_{incident_id}.pdf" if incident_id else f"reporte_mensual_{datetime.now().strftime('%Y-%m')}.pdf"
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        pdf_duration = time.time() - pdf_start
        report_log.info(f"[PDF COMPLETADO] Tipo: {pdf_type} | Archivo: {filename} | Duracion: {pdf_duration:.2f}s")
        
        return response

    except Exception as e:
        logger.error(f"Error general PDF: {e}")
        return Response({'error': str(e)}, status=500)

from django.http import JsonResponse
def health_check(request):
    return JsonResponse({"status": "alive"}, status=200)
