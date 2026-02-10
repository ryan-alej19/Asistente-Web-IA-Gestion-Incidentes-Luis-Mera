from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework import status
from .models import Incident, AnalysisCache
import hashlib
from .serializers import IncidentSerializer
from services.virustotal_service import VirusTotalService
from services.metadefender_service import MetaDefenderService
from services.gemini_service import GeminiService
from incidents.heuristic_classifier import HeuristicClassifier
import logging
import zipfile
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

logger = logging.getLogger(__name__)

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
                    if file_info.flag_bits & 0x1:  # Bit 0 = encrypted
                        logger.info(f"[ZIP] Archivo cifrado detectado: {file_info.filename}")
                        return True
                
                return False
        
        # Para RAR, 7z: solo verificar por extensión (no tenemos librería)
        elif filename.endswith(('.rar', '.7z')):
            # Heurística: archivos RAR/7z pequeños suelen ser cifrados
            return True  # Conservador
        
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
                logger.warning(f"[ZIP] Archivo cifrado detectado: {file_obj.name}")
                
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
        
        logger.info(f"Analizando archivo (Hash: {file_hash})")
        
        # Instanciar servicios
        vt_service = VirusTotalService()
        md_service = MetaDefenderService()
        gemini_service = GeminiService()
        from services.heuristic_service import HeuristicService
        heuristic_service = HeuristicService()

        # Analisis Paralelo (Optimización)
        import concurrent.futures
        
        # Failover wrappers para hilos
        def safe_vt_scan(h):
            try: return vt_service.analyze_file_hash(h)
            except Exception as e:
                logger.warning(f"[VT] Fallo: {e}")
                return {'error': str(e)}
                
        def safe_md_scan(h):
            try: return md_service.analyze_file_hash(h)
            except Exception as e:
                logger.warning(f"[MD] Fallo: {e}")
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
        if total_engines == 0:
             # Si todo fallo, retornar error
             return Response({'error': 'Todos los motores fallaron o archivo desconocido'}, status=503)
        
        detection_rate = (total_positives / total_engines * 100) if total_engines > 0 else 0
        
        if detection_rate > 70 or heuristic_result.get('risk_factor') == 'CRITICO':
            risk = 'CRITICAL'
        elif detection_rate > 30 or heuristic_result.get('risk_factor') == 'ALTO':
            risk = 'HIGH'
        elif detection_rate > 10:
            risk = 'MEDIUM'
        else:
            # Si es archivo comprimido/encriptado y tiene 0 detecciones, es sospechoso (CAUTION)
            if file_obj.name.lower().endswith(('.zip', '.rar', '.7z', '.tar', '.gz', '.encrypted')):
                risk = 'CAUTION'
            else:
                risk = 'LOW'
        
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
            
        
        return Response({
            'risk_level': risk,
            'engines': engines,
            'total_positives': total_positives,
            'total_engines': total_engines,
            'gemini_explicacion': gemini_result.get('explicacion', 'No disponible'),
            'gemini_recomendacion': gemini_result.get('recomendacion', 'Consulte con soporte')
        })
        
    except Exception as e:
        logger.error(f"[ERROR CRITICO FILE] {str(e)}")
        return Response({'error': str(e)}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_url_preview(request):
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
            logger.info(f"[CACHE] Hit para URL: {url}")
            return Response(cached_result)
            
        logger.info(f"[CACHE] Miss - Analizando URL: {url}")
        
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
            logger.warning(f"[VALIDATOR] Input rechazado: {url}")
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
            logger.warning(f"[VT] Error: {e}")
            
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
            logger.warning(f"[MD] Error: {e}")

        # 3. Google Safe Browsing
        try:
            gsb_res = gsb_service.check_url(url)
            # Aceptamos si tiene 'safe' o si 'matches' (dependiendo de implementacion interna, asumimos dict)
            is_safe = gsb_res.get('safe', True)
            
            engines_list.append({
                'name': 'Google Safe Browsing',
                'detected': not is_safe,
                'status_text': 'Seguro' if is_safe else 'Peligroso',
                'status_text': 'Seguro' if is_safe else 'Peligroso',
                'link': f"https://transparencyreport.google.com/safe-browsing/search?url={url}"
            })
            if not is_safe:
                max_positives = max(max_positives, 1)
                
        except Exception as e:
            logger.warning(f"[GSB] Error: {e}")
            
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
            logger.warning(f"[HEUR] Error: {e}")

        
        if not engines_list:
            return Response({'error': 'Todos los motores fallaron'}, status=503)
            
        # Riesgo
        if max_positives > 5:
            risk = 'CRITICAL'
            message = 'URL peligrosa'
        elif max_positives > 0:
            risk = 'MEDIUM'
            message = 'URL sospechosa'
        else:
            risk = 'LOW'
            message = 'URL segura'
            
        # Gemini (SIEMPRE)
        logger.info("[GEMINI] Iniciando analisis URL...")
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
        
        return Response(final_response)

    except Exception as e:
        logger.error(f"Error CRITICO en analisis URL: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_incident(request):
    try:
        incident_type = request.data.get('incident_type')
        
        # Recuperar datos de analisis previos si vienen en el request
        # El frontend podria enviarlos o podriamos re-calcularlos.
        # Para eficiencia en esta tesis, si el frontend ya tiene el resultado (preview),
        # lo ideal seria enviarlo.
        
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
                logger.error(f"Error parsing analysis_result JSON: {e}")
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
             # Intentar poblar campos legacy (opcional, pero util para depuracion y fallback)
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
                 logger.error(f"Error populating legacy fields: {e}")

        incident.save()
        
        return Response(IncidentSerializer(incident).data, status=201)

    except Exception as e:
        print(f"Error creating incident: {e}") # Debug
        return Response({'error': str(e)}, status=500)


from rest_framework.pagination import PageNumberPagination

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_incidents(request):
    # Lista incidentes con filtros y paginacion
    # Se puede filtrar por riesgo, estado y fechas
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
            
        # Paginación
        paginator = PageNumberPagination()
        paginator.page_size = 10
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
            
        # Si ya existe un snapshot completo, retornarlo
        if incident.analysis_result:
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
        
        # Construir resultado
        analysis_data = {
            "engines": engines,
            "gemini_explicacion": gemini_exp or "Análisis no disponible",
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
def generate_pdf_report(request, incident_id):
    # Genera un archivo PDF con el reporte del incidente
    try:
        incident = Incident.objects.get(id=incident_id)
        
        # Solo el creador o los analistas pueden ver esto
        user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
        if user_role == 'employee' and incident.reported_by != request.user:
            return Response({'error': 'No autorizado'}, status=403)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="reporte_incidente_{incident.id}.pdf"'

        p = canvas.Canvas(response, pagesize=letter)
        w, h = letter

        # --- LOGO ---
        import os
        from django.conf import settings
        # Ruta al logo: ../frontend/public/assets/logo_tecnicontrol.jpg
        # Asumiendo BASE_DIR es backend/
        logo_path = os.path.join(settings.BASE_DIR, '..', 'frontend', 'public', 'assets', 'logo_tecnicontrol.jpg')
        if os.path.exists(logo_path):
            try:
                # Dibujar logo (x, y, width, height)
                # Aspect ratio aprox 2:1? Ajustar segun necesidad
                p.drawImage(logo_path, 50, h - 100, width=150, height=75, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                logger.warning(f"No se pudo cargar logo PDF: {e}")
        else:
            logger.warning(f"Logo no encontrado en: {logo_path}")

        # Encabezado Corregido (Desplazado por el logo)
        p.setFont("Helvetica-Bold", 18)
        p.drawString(220, h - 60, "REPORTE DE INCIDENTE")
        p.setFont("Helvetica-Bold", 12)
        p.drawString(220, h - 80, "TECNICONTROL AUTOMOTRIZ")
        
        p.setFont("Helvetica", 10)
        p.drawString(50, h - 130, f"ID Incidente: #{incident.id}")
        p.drawString(300, h - 130, f"Fecha: {incident.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        p.drawString(50, h - 145, f"Reportado por: {incident.reported_by.username}")
        p.drawString(300, h - 145, f"Estado: {incident.status.upper()}")
        
        # Linea separadora
        p.line(50, h - 160, 550, h - 160)
        
        y = h - 200
        p.setFont("Helvetica-Bold", 14)
        p.drawString(50, y, "Resumen del Análisis")
        y -= 30
        
        p.setFont("Helvetica", 11)
        p.drawString(50, y, f"Tipo de Incidente: {incident.incident_type.upper()}")
        y -= 20
        target = incident.url or (incident.attached_file.name if incident.attached_file else "Desconocido")
        # Cortar target si es muy largo
        if len(target) > 70: target = target[:67] + "..."
        p.drawString(50, y, f"Objetivo Analizado: {target}")
        y -= 20
        
        # Riesgo con color? (No facil en PDF simple, usamos texto)
        p.drawString(50, y, f"Nivel de Riesgo Evaluado: {incident.risk_level}")
        y -= 30
        
        # Resultados Tecnicos
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Motores de Seguridad")
        y -= 20
        p.setFont("Helvetica", 11)

        # Intentar obtener snapshot
        positives = 0
        total = 0
        if incident.analysis_result:
             positives = incident.analysis_result.get('positives', incident.analysis_result.get('total_positives', 0))
             total = incident.analysis_result.get('total', incident.analysis_result.get('total_engines', 0))
        elif incident.virustotal_result:
             positives = incident.virustotal_result.get('positives', 0)
             total = incident.virustotal_result.get('total', 0)
        
        p.drawString(50, y, f"Detecciones: {positives} / {total}")
        y -= 20
        p.drawString(50, y, f"Motores Consultados: VirusTotal, MetaDefender, Google Safe Browsing")
        y -= 40

        # Analisis IA
        if incident.gemini_analysis or (incident.analysis_result and incident.analysis_result.get('gemini_explicacion')):
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y, "Informe de Inteligencia Artificial (Gemini)")
            y -= 20
            p.setFont("Helvetica-Oblique", 10)
            
            text = incident.gemini_analysis or incident.analysis_result.get('gemini_explicacion')
            
            # Wrap text simple
            from textwrap import wrap
            lines = wrap(text, width=90)
            
            for line in lines:
                 if y < 50:
                     p.showPage()
                     y = h - 50
                     p.setFont("Helvetica-Oblique", 10)
                 p.drawString(50, y, line)
                 y -= 15
            
            y -= 10
            # Recomendacion
            rec = incident.analysis_result.get('gemini_recomendacion') if incident.analysis_result else None
            if rec:
                p.setFont("Helvetica-Bold", 10)
                p.drawString(50, y, "Recomendación:")
                y -= 15
                p.setFont("Helvetica", 10)
                lines = wrap(rec, width=90)
                for line in lines:
                    if y < 50:
                        p.showPage()
                        y = h - 50
                    p.drawString(50, y, line)
                    y -= 15

        # Footer
        p.setFont("Helvetica-Oblique", 8)
        p.drawString(50, 30, "Reporte generado por Asistente de Ciberseguridad - Tecnicontrol Automotriz")
        p.drawString(400, 30, f"Página {p.getPageNumber()}")
        
        p.showPage()
        p.save()
        return response

    except Incident.DoesNotExist:
        return Response({'error': 'Incidente no encontrado'}, status=404)
    except Exception as e:
        logger.error(f"Error generando PDF: {e}")
        return Response({'error': str(e)}, status=500)
