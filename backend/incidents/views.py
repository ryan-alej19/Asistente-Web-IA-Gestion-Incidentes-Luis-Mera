from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def analyze_incident(request):
    try:
        data = json.loads(request.body)
        desc = data.get('description', '').lower().strip()

        tipo = 'OTRO'
        crit = 'BAJO'
        recomendacion = 'No se identifican incidentes. Continúe con sus funciones habituales.'
        tecnico = 'Ningún síntoma ni patrón asociado a amenazas detectado en la descripción.'

        # - Mensajes para errores, irrelevancias o pruebas
        if not desc or desc in ['hola', 'buenos días', 'prueba', 'test', 'agua', 'ninguno', 'nada']:
            tipo = 'NINGUNA'
            crit = 'BAJO'
            recomendacion = 'No se detecta amenaza ni riesgo. Puede seguir con su trabajo.'
            tecnico = 'Esta entrada no presenta riesgos de seguridad informática.'
        elif any(x in desc for x in ['banco', 'enlace', 'login', 'clave', 'contrasena', 'phishing']):
            tipo = 'PHISHING'
            crit = 'ALTO'
            recomendacion = 'No haga clic ni responda. Reporte a TI inmediatamente.'
            tecnico = 'Detectado patrón de probable phishing o intento fraudulento.'
        elif any(x in desc for x in ['descarga', 'archivo', 'malware', 'virus']):
            tipo = 'MALWARE'
            crit = 'CRÍTICO'
            recomendacion = 'Aísle su equipo y contacte soporte técnico.'
            tecnico = 'Palabras clave vinculadas a software malicioso o infección.'
        elif any(x in desc for x in ['transferencia', 'dinero', 'urgente', 'ceo', 'ingeniería social']):
            tipo = 'INGENIERÍA_SOCIAL'
            crit = 'CRÍTICO'
            recomendacion = 'Verifique la identidad. No continúe sin confirmar con el área responsable.'
            tecnico = 'Posible ingeniería social o suplantación de autoridad detectada.'
        elif any(x in desc for x in ['proveedor', 'ransomware']):
            tipo = 'RANSOMWARE'
            crit = 'CRÍTICO'
            recomendacion = 'Aísle el sistema, no pague rescate y contacte a TI de inmediato.'
            tecnico = 'Indicadores de posible ataque ransomware.'

        response = {
            "success": True,
            "incident_id": 999,
            "analysis": {
                "threat_type": tipo,
                "criticality": crit,
                "confidence": 0.99 if tipo not in ['OTRO', 'NINGUNA'] else 0.85,
                "recommendation": recomendacion,
                "technical_details": tecnico
            }
        }
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "incident_id": 0,
            "analysis": {
                "threat_type": "OTRO",
                "criticality": "MEDIO",
                "confidence": 0.5,
                "recommendation": "Error inesperado. Contactar soporte técnico.",
                "technical_details": f"Error Python: {str(e)}"
            }
        })

@csrf_exempt
def get_incidents(request):
    fake_incidents = [
        {"id": 1, "threat_type": "PHISHING", "criticality": "ALTO", "resolved": False, "created_at": "2024-11-02T22:00:00Z", "confidence_score": 0.92},
        {"id": 2, "threat_type": "MALWARE", "criticality": "CRÍTICO", "resolved": True, "created_at": "2024-11-02T21:30:00Z", "confidence_score": 0.87},
        {"id": 3, "threat_type": "ACCESO_ANÓMALO", "criticality": "MEDIO", "resolved": False, "created_at": "2024-11-02T21:00:00Z", "confidence_score": 0.75},
    ]
    return JsonResponse(fake_incidents, safe=False)
@csrf_exempt
def get_dashboard_stats(request):
    """API para estadísticas del dashboard administrativo"""
    stats = {
        "total_incidents": 47,
        "critical_incidents": 8,
        "resolved_incidents": 32,
        "pending_incidents": 15,
        "incidents_by_type": {
            "PHISHING": 18,
            "MALWARE": 12,
            "INGENIERÍA_SOCIAL": 8,
            "RANSOMWARE": 5,
            "ACCESO_ANÓMALO": 3,
            "OTRO": 1
        },
        "incidents_by_month": [
            {"month": "Ago", "count": 12},
            {"month": "Sep", "count": 18},
            {"month": "Oct", "count": 17},
        ],
        "recent_activity": [
            {"id": 47, "type": "PHISHING", "date": "2024-11-03", "status": "PENDIENTE"},
            {"id": 46, "type": "MALWARE", "date": "2024-11-02", "status": "RESUELTO"},
            {"id": 45, "type": "INGENIERÍA_SOCIAL", "date": "2024-11-02", "status": "INVESTIGANDO"},
        ]
    }
    return JsonResponse(stats)

@csrf_exempt
def update_incident_status(request):
    """API para actualizar estado de incidentes"""
    if request.method == 'POST':
        data = json.loads(request.body)
        incident_id = data.get('incident_id')
        new_status = data.get('status')
        
        # Simulamos actualización exitosa
        return JsonResponse({
            "success": True,
            "message": f"Incidente {incident_id} actualizado a {new_status}",
            "incident_id": incident_id,
            "status": new_status
        })
    
    return JsonResponse({"error": "Método no permitido"}, status=405)