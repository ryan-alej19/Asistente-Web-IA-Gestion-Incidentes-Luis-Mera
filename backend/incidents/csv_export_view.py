import csv
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Incident

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def export_incidents_csv(request):
    """
    Exporta todos los incidentes a CSV con 18 columnas.
    Solo accesible para analistas y administradores.
    """
    # Verificar que el usuario sea analista o admin
    user_role = getattr(request.user, 'profile', None) and request.user.profile.role or 'employee'
    
    if user_role not in ['analyst', 'admin']:
        return Response(
            {'error': 'No tienes permiso para exportar datos'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Filtros opcionales
    incident_type = request.GET.get('type', None)
    risk_level = request.GET.get('risk_level', None)
    status_filter = request.GET.get('status', None)
    
    # Query base
    incidents = Incident.objects.all().select_related('reported_by')
    
    # Aplicar filtros si existen
    if incident_type and incident_type != 'all':
        incidents = incidents.filter(incident_type=incident_type)
    if risk_level:
        incidents = incidents.filter(risk_level=risk_level)
    if status_filter:
        incidents = incidents.filter(status=status_filter)
    
    # Ordenar por fecha de creación descendente
    incidents = incidents.order_by('-created_at')
    
    # Crear respuesta HTTP con tipo CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="incidentes_talleres_luis_mera.csv"'
    
    # Crear writer CSV
    writer = csv.writer(response)
    
    # HEADER con 18 columnas
    writer.writerow([
        'ID',
        'Fecha Creación',
        'Fecha Actualización',
        'Usuario Reportante',
        'Tipo Incidente',
        'URL/Archivo',
        'Descripción',
        'Estado',
        'Nivel Riesgo Auto',
        'Nivel Riesgo Analista',
        'IP Origen',
        'Clasificación Heurística',
        'VirusTotal Detecciones',
        'VirusTotal Total',
        'MetaDefender Resultado',
        'Safe Browsing Resultado',
        'Gemini Explicación',
        'Gemini Recomendación'
    ])
    
    # DATOS
    for inc in incidents:
        # Parsear analysis_result si existe
        vt_detections = ''
        vt_total = ''
        md_result = ''
        gsb_result = ''
        gemini_explanation = ''
        gemini_recommendation = ''
        
        if inc.analysis_result:
            import json
            result = inc.analysis_result if isinstance(inc.analysis_result, dict) else {}
            if isinstance(inc.analysis_result, str):
                 try:
                     result = json.loads(inc.analysis_result)
                 except: set()

            
            # VirusTotal (adaptado a estructura actual)
            # engines es una lista en la estructura actual
            engines = result.get('engines', [])
            vt_data = next((e for e in engines if e['name'] == 'VirusTotal'), None)
            if vt_data:
                vt_detections = vt_data.get('positives', 0)
                vt_total = vt_data.get('total', 0)
            
            # MetaDefender
            md_data = next((e for e in engines if e['name'] == 'MetaDefender'), None)
            if md_data:
                md_result = f"{md_data.get('positives', 0)}/{md_data.get('total', 0)}"

            # Safe Browsing
            gsb_data = next((e for e in engines if e['name'] == 'Google Safe Browsing'), None)
            if gsb_data:
                 gsb_result = gsb_data.get('status_text', '')
            
            # Gemini
            gemini_explanation = result.get('gemini_explicacion', '')
            gemini_recommendation = result.get('gemini_recomendacion', '')
        
        # Heuristica (Legacy field or derived?)
        # En el modelo actual no veo heuristic_classification en Incident, quizas se guarda en analysis_result o notas
        # Lo dejare vacio si no existe atributo directo
        heuristic_val = ''
        
        writer.writerow([
            inc.id,
            inc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            inc.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            inc.reported_by.username,
            inc.incident_type,
            inc.url or (inc.attached_file.name if inc.attached_file else '') or '',
            inc.description or '',
            inc.status,
            inc.risk_level or '',
            '', # inc.analyst_risk_level no existe en modelo verificado
            '', # inc.source_ip no existe en modelo verificado
            heuristic_val,
            vt_detections,
            vt_total,
            md_result,
            gsb_result,
            gemini_explanation,
            gemini_recommendation
        ])
    
    return response
