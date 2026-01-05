"""
Clasificador de incidentes basado en reglas heurísticas
IA EXPLICABLE Y DEFENDIBLE PARA TESIS ACADÉMICA
"""
from typing import Dict, Any, Tuple
from ia_classifier.classifier import ThreatClassifier


class IncidentClassifier:
    """
    Clasificador de incidentes de seguridad basado en reglas heurísticas.
    
    Estrategia académica:
    1. Analiza palabras clave en la descripción
    2. Asigna puntuación según severidad detectada
    3. Retorna clasificación con confianza limitada (<70%)
    4. Complementado con VirusTotal y Gemini
    """
    
    def __init__(self):
        """Inicializa palabras clave basadas en estándares (NIST, ISO, MITRE)"""
        
        self.CRITICAL_KEYWORDS = [
            'ransomware', 'malware', 'virus', 'trojan', 'troyano', 'backdoor',
            'breach', 'robo de datos', 'exfiltracion', 'exfiltración',
            'encriptado', 'cifrado malicioso', 'secuestro',
            'botnet', 'apt', 'zero-day', 'exploit',
        ]
        
        self.HIGH_KEYWORDS = [
            'hack', 'hacking', 'unauthorized', 'no autorizado',
            'phishing', 'suplantacion', 'correo sospechoso',
            'fuerza bruta', 'brute force', 'sql injection', 'xss',
            'ddos', 'denegacion de servicio',
        ]
        
        self.MEDIUM_KEYWORDS = [
            'error', 'fallo', 'mal configurado',
            'warning', 'advertencia', 'alerta',
            'timeout', 'conexion fallida', 'cuenta bloqueada',
        ]
        
        self.INCIDENT_TYPE_SEVERITY = {
            'malware': ('critical', 0.70),
            'ransomware': ('critical', 0.75),
            'robo_datos': ('critical', 0.75),
            'phishing': ('high', 0.65),
            'ddos': ('high', 0.70),
            'error_configuracion': ('medium', 0.45),
            'otro': ('low', 0.30),
        }
    
    def _normalize_text(self, text: str) -> str:
        """Normaliza texto para comparación."""
        text = text.lower()
        replacements = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','ñ':'n'}
        for old, new in replacements.items():
            text = text.replace(old, new)
        return ' '.join(text.split())  # Eliminar espacios múltiples
    
    def classify(self, description: str, threat_type: str = 'otro') -> Tuple[str, float]:
        """
        Clasifica un incidente en base a descripción y tipo.
        
        Returns:
            tuple: (severity, confidence)
            - severity: 'low' | 'medium' | 'high' | 'critical'
            - confidence: float entre 0.0 y 0.70
        """
        if not description or len(description.strip()) < 5:
            return ('low', 0.20)
        
        text = self._normalize_text(description)
        threat_type_lower = self._normalize_text(threat_type)
        
        # Conteo de coincidencias
        critical_matches = sum(1 for kw in self.CRITICAL_KEYWORDS if kw in text)
        high_matches = sum(1 for kw in self.HIGH_KEYWORDS if kw in text)
        medium_matches = sum(1 for kw in self.MEDIUM_KEYWORDS if kw in text)
        
        # Lógica de decisión
        if critical_matches > 0:
            confidence = min(0.70, 0.55 + (critical_matches * 0.05))
            return ('critical', round(confidence, 2))
        
        if threat_type_lower in self.INCIDENT_TYPE_SEVERITY:
            severity, confidence = self.INCIDENT_TYPE_SEVERITY[threat_type_lower]
            if severity == 'critical':
                return (severity, confidence)
        
        if high_matches > 0:
            confidence = min(0.70, 0.50 + (high_matches * 0.04))
            return ('high', round(confidence, 2))
        
        if threat_type_lower in self.INCIDENT_TYPE_SEVERITY:
            severity, confidence = self.INCIDENT_TYPE_SEVERITY[threat_type_lower]
            if severity == 'high':
                return (severity, confidence)
        
        if medium_matches > 0:
            confidence = min(0.70, 0.35 + (medium_matches * 0.03))
            return ('medium', round(confidence, 2))
        
        if threat_type_lower in self.INCIDENT_TYPE_SEVERITY:
            severity, confidence = self.INCIDENT_TYPE_SEVERITY[threat_type_lower]
            if severity == 'medium':
                return (severity, confidence)
        
        return ('low', 0.25)
    
    def get_explanation(self, severity: str, confidence: float) -> Dict[str, Any]:
        """
        Genera explicación en español de la clasificación.
        Útil para dashboard y defensa oral.
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
            'confidence_note': 'Sistema de reglas heurísticas (confianza limitada)',
            'description': (
                f"Incidente clasificado como {severity_text.get(severity)} "
                f"con {confidence_pct} de confianza basado en análisis de palabras clave."
            ),
            'recommendation': (
                'Se recomienda validar con VirusTotal (URLs) o Gemini (contexto) '
                'para confirmar la clasificación inicial.'
            )
        }


# Funciones legacy (compatibilidad)
def classify_incident(title: str, description: str, incident_type: str = '') -> tuple:
    """Función legacy para compatibilidad."""
    classifier = IncidentClassifier()
    severity, confidence = classifier.classify(description, incident_type)
    
    threat_type_map = {
        'critical': 'Malware/Ransomware/Breach',
        'high': 'Phishing/Unauthorized Access',
        'medium': 'Configuration Error',
        'low': 'Other/Unknown'
    }
    
    threat_type = threat_type_map.get(severity, 'Unknown')
    return (severity, confidence, threat_type)


def get_classification_explanation(severity: str, confidence: float, threat_type: str) -> Dict[str, Any]:
    """Función legacy para compatibilidad."""
    classifier = IncidentClassifier()
    explanation = classifier.get_explanation(severity, confidence)
    explanation['threat_type'] = threat_type
    return explanation
