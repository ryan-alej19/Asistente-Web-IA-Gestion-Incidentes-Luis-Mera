"""
Clasificador de incidentes basado en reglas simples
EXPLICABLE Y DEFENDIBLE PARA LA TESIS

Argumentación académica:
- No usa machine learning complejo
- Basado en palabras clave definidas por estándares (NIST, ISO 27035)
- Resultado reproducible y auditable
- Fácil de explicar en defensa oral
"""


class IncidentClassifier:
    """
    Clasificador de incidentes de seguridad basado en palabras clave.
    Versión orientada a objetos compatible con views.py
    """
    
    def __init__(self):
        """Inicializa las palabras clave de clasificación"""
        
        # ===== PALABRAS CLAVE POR SEVERIDAD =====
        # Basadas en NIST SP 800-61 y estándares de seguridad
        
        self.CRITICAL_KEYWORDS = [
            'ransomware', 'malware', 'virus', 'breach', 'robo de datos',
            'encriptado', 'crypto', 'botnet', 'ataque crítico', 'criptografía',
            'exfiltración', 'datos sensibles', 'base de datos comprometida',
            'ciberataque masivo', 'ataques dirigidos',
            'backdoor', 'exploit', 'zero-day', 'vulnerabilidad crítica',
            'administrador comprometido', 'privilegios elevados no autorizados',
        ]
        
        self.HIGH_KEYWORDS = [
            'hack', 'unauthorized', 'no autorizado', 'phishing', 'sospechoso',
            'suspicious', 'login anómalo', 'acceso extraño', 'fuerza bruta',
            'intento de ingreso', 'contraseña capturada', 'credential stuffing',
            'privilege escalation', 'acceso no autorizado a datos',
            'inyección sql', 'cross-site', 'xss', 'ddos', 'ataque de negación',
            'modificación no autorizada', 'conexión sospechosa',
        ]
        
        self.MEDIUM_KEYWORDS = [
            'error', 'fallo', 'incorrecto', 'warning', 'advertencia',
            'timeout', 'conexión fallida', 'falla de sistema',
            'configuración errónea', 'acceso incorrecto',
            'intento fallido', 'cuenta bloqueada',
        ]
        
        # ===== TIPO DE INCIDENTE =====
        self.INCIDENT_TYPE_SEVERITY = {
            'malware': ('critical', 0.85),
            'ransomware': ('critical', 0.90),
            'phishing': ('high', 0.75),
            'acceso_sospechoso': ('high', 0.70),
            'ddos': ('high', 0.80),
            'robo_datos': ('critical', 0.85),
            'error_configuracion': ('medium', 0.50),
            'otro': ('medium', 0.50),
        }
    
    def classify(self, description, threat_type='otro'):
        """
        Clasifica un incidente de seguridad en base a su descripción.
        
        Args:
            description (str): Descripción del incidente
            threat_type (str): Tipo de amenaza (phishing, malware, ransomware, etc.)
        
        Returns:
            tuple: (severity, confidence)
            - severity: 'low', 'medium', 'high', 'critical'
            - confidence: float entre 0.0 y 1.0
        
        Lógica:
        1. Busca palabras clave que indiquen severidad
        2. Asigna puntuación según cantidad y tipo de palabras
        3. Considera el tipo de incidente si fue especificado
        4. Retorna clasificación defendible
        """
        
        # ===== NORMALIZACIÓN DE TEXTO =====
        text = description.lower()
        text = text.replace('á', 'a').replace('é', 'e').replace('í', 'i')
        text = text.replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n')
        
        # ===== CONTAR COINCIDENCIAS =====
        critical_matches = sum(1 for word in self.CRITICAL_KEYWORDS if word in text)
        high_matches = sum(1 for word in self.HIGH_KEYWORDS if word in text)
        medium_matches = sum(1 for word in self.MEDIUM_KEYWORDS if word in text)
        
        # ===== LÓGICA DE DECISIÓN =====
        
        # Normalizar tipo de incidente
        threat_type_lower = threat_type.lower() if threat_type else ''
        
        # REGLA 1: Si hay coincidencias críticas
        if critical_matches > 0:
            confidence = min(0.95, 0.70 + critical_matches * 0.10)
            return ('critical', confidence)
        
        # REGLA 2: Si hay coincidencias altas o el tipo es peligroso
        if high_matches > 0 or 'phishing' in text or 'phishing' in threat_type_lower:
            confidence = min(0.90, 0.60 + high_matches * 0.10)
            return ('high', confidence)
        
        # REGLA 3: Si el tipo de incidente indica algo crítico
        if threat_type_lower in self.INCIDENT_TYPE_SEVERITY:
            severity, confidence = self.INCIDENT_TYPE_SEVERITY[threat_type_lower]
            if severity in ['critical', 'high']:
                return (severity, confidence)
        
        # REGLA 4: Si hay coincidencias medianas
        if medium_matches > 0:
            confidence = min(0.75, 0.40 + medium_matches * 0.10)
            return ('medium', confidence)
        
        # REGLA 5: Por defecto, bajo riesgo
        return ('low', 0.30)
    
    def get_explanation(self, severity, confidence):
        """
        Retorna una explicación en español de por qué se clasificó así.
        Útil para el dashboard y defensa oral.
        
        Args:
            severity (str): Severidad calculada
            confidence (float): Confianza de la clasificación
        
        Returns:
            dict: Diccionario con información de la clasificación
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
            'description': f"Incidente clasificado como {severity_text.get(severity)} con {confidence_pct} de confianza."
        }


# ===== FUNCIONES LEGACY (para compatibilidad con código antiguo) =====

def classify_incident(title, description, incident_type=''):
    """
    Función legacy que usa la clase IncidentClassifier internamente.
    Se mantiene para compatibilidad con código antiguo.
    
    Returns:
        tuple: (severity, confidence, threat_type)
    """
    classifier = IncidentClassifier()
    severity, confidence = classifier.classify(description, incident_type)
    
    # Determinar tipo de amenaza basado en severidad
    threat_type_map = {
        'critical': 'Malware/Ransomware/Breach',
        'high': 'Phishing/Unauthorized Access',
        'medium': 'Configuration Error/System Issue',
        'low': 'Other/Unknown'
    }
    
    threat_type = threat_type_map.get(severity, 'Unknown')
    return (severity, confidence, threat_type)


def get_classification_explanation(severity, confidence, threat_type):
    """
    Función legacy que usa la clase IncidentClassifier internamente.
    Se mantiene para compatibilidad con código antiguo.
    """
    classifier = IncidentClassifier()
    explanation = classifier.get_explanation(severity, confidence)
    explanation['threat_type'] = threat_type
    return explanation
