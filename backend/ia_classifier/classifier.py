"""
Clasificador de incidentes basado en reglas simples
EXPLICABLE Y DEFENDIBLE PARA LA TESIS

Argumentación académica:
- No usa machine learning complejo
- Basado en palabras clave definidas por estándares (NIST, ISO 27035)
- Resultado reproducible y auditable
- Fácil de explicar en defensa oral
"""

def classify_incident(title, description, incident_type=''):
    """
    Clasifica un incidente de seguridad en base a su descripción.
    
    Retorna:
        tuple: (severity, confidence, threat_type)
        - severity: 'low', 'medium', 'high', 'critical'
        - confidence: float entre 0.0 y 1.0
        - threat_type: string descriptivo del tipo de amenaza
    
    Lógica:
    1. Busca palabras clave que indiquen severidad
    2. Asigna puntuación según cantidad y tipo de palabras
    3. Considera el tipo de incidente si fue especificado
    4. Retorna clasificación defendible
    """
    
    # ===== PALABRAS CLAVE POR SEVERIDAD =====
    # Basadas en NIST SP 800-61 y estándares de seguridad
    
    CRITICAL_KEYWORDS = [
        'ransomware', 'malware', 'virus', 'breach', 'robo de datos',
        'encriptado', 'crypto', 'botnet', 'ataque crítico', 'criptografía',
        'exfiltración', 'datos sensibles', 'base de datos comprometida',
        'allá of ransomware', 'ciberataque masivo', 'ataques dirigidos',
        'backdoor', 'exploit', 'zero-day', 'vulnerabilidad crítica',
        'administrador comprometido', 'privilegios elevados no autorizados',
    ]
    
    HIGH_KEYWORDS = [
        'hack', 'unauthorized', 'no autorizado', 'phishing', 'sospechoso',
        'suspicious', 'login anómalo', 'acceso extraño', 'fuerza bruta',
        'intento de ingreso', 'contraseña capturada', 'credential stuffing',
        'privilege escalation', 'acceso no autorizado a datos',
        'inyección sql', 'cross-site', 'xss', 'ddos', 'ataque de negación',
        'modificación no autorizada', 'conexión sospechosa',
    ]
    
    MEDIUM_KEYWORDS = [
        'error', 'fallo', 'incorrecto', 'warning', 'advertencia',
        'timeout', 'conexión fallida', 'falla de sistema',
        'configuración errónea', 'acceso incorrecto',
        'intento fallido', 'cuenta bloqueada',
    ]
    
    # ===== TIPO DE INCIDENTE =====
    INCIDENT_TYPE_SEVERITY = {
        'malware': ('critical', 0.85),
        'ransomware': ('critical', 0.90),
        'phishing': ('high', 0.75),
        'acceso_sospechoso': ('high', 0.70),
        'ddos': ('high', 0.80),
        'robo_datos': ('critical', 0.85),
        'error_configuracion': ('medium', 0.50),
        'otro': ('medium', 0.50),
    }
    
    # ===== NORMALIZACIÓN DE TEXTO =====
    text = (title + ' ' + description).lower()
    text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
    text = text.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
    
    # ===== CONTAR COINCIDENCIAS =====
    critical_matches = sum(1 for word in CRITICAL_KEYWORDS if word in text)
    high_matches = sum(1 for word in HIGH_KEYWORDS if word in text)
    medium_matches = sum(1 for word in MEDIUM_KEYWORDS if word in text)
    
    # ===== LÓGICA DE DECISIÓN =====
    
    # Si el tipo de incidente está especificado
    incident_type_lower = incident_type.lower() if incident_type else ''
    
    # REGLA 1: Si hay coincidencias críticas
    if critical_matches > 0:
        confidence = min(0.95, 0.70 + critical_matches * 0.10)
        threat_type = 'Malware/Ransomware/Breach'
        return ('critical', confidence, threat_type)
    
    # REGLA 2: Si hay coincidencias altas o el tipo es peligroso
    if high_matches > 0 or 'phishing' in text or 'phishing' in incident_type_lower:
        confidence = min(0.90, 0.60 + high_matches * 0.10)
        threat_type = 'Phishing/Unauthorized Access'
        return ('high', confidence, threat_type)
    
    # REGLA 3: Si el tipo de incidente indica algo crítico
    if incident_type_lower in INCIDENT_TYPE_SEVERITY:
        severity, confidence = INCIDENT_TYPE_SEVERITY[incident_type_lower]
        if severity == 'critical':
            threat_type = 'Threat Type: ' + incident_type
            return ('critical', confidence, threat_type)
        elif severity == 'high':
            threat_type = 'Threat Type: ' + incident_type
            return ('high', confidence, threat_type)
    
    # REGLA 4: Si hay coincidencias medianas
    if medium_matches > 0:
        confidence = min(0.75, 0.40 + medium_matches * 0.10)
        threat_type = 'Configuration Error/System Issue'
        return ('medium', confidence, threat_type)
    
    # REGLA 5: Por defecto, bajo riesgo
    threat_type = 'Other/Unknown'
    return ('low', 0.30, threat_type)


def get_classification_explanation(severity, confidence, threat_type):
    """
    Retorna una explicación en español de por qué se clasificó así.
    Ústil para el dashboard y defensa oral.
    """
    severity_text = {
        'low': 'Bajo - Riesgo mínimo',
        'medium': 'Medio - Requiere seguimiento',
        'high': 'Alto - Acción inmediata necesaria',
        'critical': 'Crítico - ACCIÓN URGENTE',
    }
    
    confidence_pct = f"{confidence * 100:.0f}%"
    
    return {
        'severity': severity_text.get(severity, 'Desconocido'),
        'confidence': confidence_pct,
        'threat_type': threat_type,
        'description': f"Incidente clasificado como {severity_text.get(severity)} con {confidence_pct} de confianza. Tipo de amenaza: {threat_type}"
    }
