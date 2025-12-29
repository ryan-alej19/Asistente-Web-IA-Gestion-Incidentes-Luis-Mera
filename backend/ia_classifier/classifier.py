"""
Clasificador de incidentes con IA simple
Usa reglas de palabras clave sin modelos de ML pesados
"""

from .rules import IncidentClassificationRules


class IncidentClassifier:
    """
    Clasificador de incidentes de ciberseguridad
    Método: Análisis de palabras clave (sin ML)
    """
    
    def __init__(self):
        self.rules = IncidentClassificationRules()
    
    def classify(self, description: str, threat_type: str = None) -> tuple:
        """
        Clasifica un incidente y retorna severidad + confianza
        
        Args:
            description (str): Descripción del incidente
            threat_type (str): Tipo de amenaza sugerido (phishing, malware, etc)
            
        Returns:
            tuple: (severity, confidence)
                - severity: 'low', 'medium', 'high', 'critical'
                - confidence: float entre 0.0 y 1.0
                
        Example:
            >>> classifier = IncidentClassifier()
            >>> severity, confidence = classifier.classify(
            ...     "Email sospechoso pidiendo verificar contraseña",
            ...     "phishing"
            ... )
            >>> print(f"Severidad: {severity}, Confianza: {confidence}")
            Severidad: high, Confianza: 0.85
        """
        
        # Validación básica
        if not description or not isinstance(description, str):
            return ('low', 0.3)
        
        # Si no se proporciona threat_type, detectarlo
        if not threat_type:
            threat_type = self.rules.classify_threat_type(description)
        
        # Calcular severidad
        severity = self.rules.calculate_severity(description, threat_type)
        
        # Calcular confianza
        confidence = self.rules.calculate_confidence(description, threat_type)
        
        return (severity, confidence)
    
    def analyze(self, description: str) -> dict:
        """
        Análisis completo de un incidente
        
        Args:
            description (str): Descripción del incidente
            
        Returns:
            dict: Diccionario con análisis completo
        """
        threat_type = self.rules.classify_threat_type(description)
        severity, confidence = self.classify(description, threat_type)
        
        return {
            'threat_type': threat_type,
            'severity': severity,
            'confidence': confidence,
            'description': description
        }
