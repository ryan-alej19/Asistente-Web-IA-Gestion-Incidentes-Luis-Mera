"""
Reglas simples de clasificación de incidentes por IA
Sin modelos complejos - solo lógica de búsqueda de palabras clave
"""

class IncidentClassificationRules:
    """Reglas para clasificar incidentes basadas en palabras clave"""
    
    # Palabras clave por tipo de amenaza
    PHISHING_KEYWORDS = [
        'verificar cuenta', 'actualizar contraseña', 'confirmar identidad',
        'urgente', 'acción requerida', 'click aqui', 'valida tu', 'confirma tu',
        'enlace sospechoso', 'email falso', 'usuario no autorizado'
    ]
    
    MALWARE_KEYWORDS = [
        'virus', 'troyano', 'ransomware', 'spyware', 'malware',
        'executable descargado', 'archivo sospechoso', 'código malicioso',
        'infección', 'detectado'
    ]
    
    ACCESO_SOSPECHOSO_KEYWORDS = [
        'acceso no autorizado', 'login fallido', 'intento de conexión',
        'brute force', 'fuerza bruta', 'múltiples intentos', 'ip desconocida',
        'ubicación anómala', 'horario inusual'
    ]
    
    OTRO_KEYWORDS = [
        'vulnerabilidad', 'exploit', 'fuera de servicio', 'ataque',
        'dato sensible', 'infracción', 'perdida de datos'
    ]

    @staticmethod
    def classify_threat_type(description: str) -> str:
        """
        Detecta el tipo de amenaza basándose en palabras clave
        
        Args:
            description: Descripción del incidente
            
        Returns:
            str: Tipo de amenaza detectado (phishing, malware, acceso_sospechoso, otro)
        """
        description_lower = description.lower()
        
        # Contar coincidencias en cada categoría
        phishing_count = sum(1 for keyword in IncidentClassificationRules.PHISHING_KEYWORDS 
                            if keyword in description_lower)
        malware_count = sum(1 for keyword in IncidentClassificationRules.MALWARE_KEYWORDS 
                           if keyword in description_lower)
        acceso_count = sum(1 for keyword in IncidentClassificationRules.ACCESO_SOSPECHOSO_KEYWORDS 
                          if keyword in description_lower)
        otro_count = sum(1 for keyword in IncidentClassificationRules.OTRO_KEYWORDS 
                        if keyword in description_lower)
        
        # Retornar el tipo con más coincidencias
        max_count = max(phishing_count, malware_count, acceso_count, otro_count)
        
        if max_count == 0:
            return 'otro'
        elif phishing_count == max_count:
            return 'phishing'
        elif malware_count == max_count:
            return 'malware'
        elif acceso_count == max_count:
            return 'acceso_sospechoso'
        else:
            return 'otro'

    @staticmethod
    def calculate_severity(description: str, threat_type: str) -> str:
        """
        Calcula la severidad basándose en palabras clave críticas
        
        Args:
            description: Descripción del incidente
            threat_type: Tipo de amenaza
            
        Returns:
            str: Severidad (low, medium, high, critical)
        """
        description_lower = description.lower()
        
        # Palabras clave para severidad crítica
        critical_keywords = [
            'crítico', 'urgente', 'inmediato', 'datos sensibles', 'datos financieros',
            'pérdida de datos', 'acceso total', 'compromiso total', 'ransomware',
            'múltiples afectados'
        ]
        
        # Palabras clave para severidad alta
        high_keywords = [
            'grave', 'importante', 'múltiples', 'afectados', 'sistema caido',
            'acceso no autorizado', 'brute force', 'explorado'
        ]
        
        # Contar coincidencias
        critical_count = sum(1 for keyword in critical_keywords if keyword in description_lower)
        high_count = sum(1 for keyword in high_keywords if keyword in description_lower)
        
        # Determinar severidad por tipo si es una amenaza seria
        if critical_count > 0 or threat_type == 'malware':
            return 'critical'
        elif high_count > 0 or threat_type == 'phishing':
            return 'high'
        elif threat_type == 'acceso_sospechoso':
            return 'medium'
        else:
            return 'low'

    @staticmethod
    def calculate_confidence(description: str, threat_type: str) -> float:
        """
        Calcula la confianza de la clasificación (0.0 - 1.0)
        
        Args:
            description: Descripción del incidente
            threat_type: Tipo de amenaza
            
        Returns:
            float: Confianza de 0.0 a 1.0
        """
        description_lower = description.lower()
        
        # Base de confianza según el tipo
        base_confidence = {
            'phishing': 0.75,
            'malware': 0.80,
            'acceso_sospechoso': 0.70,
            'otro': 0.50
        }
        
        confidence = base_confidence.get(threat_type, 0.5)
        
        # Aumentar confianza si la descripción es larga y detallada
        if len(description) > 100:
            confidence = min(1.0, confidence + 0.1)
        
        # Aumentar confianza si contiene detalles técnicos
        technical_terms = ['ip', 'puerto', 'usuario', 'email', 'url', 'archivo', 'hash']
        technical_count = sum(1 for term in technical_terms if term in description_lower)
        if technical_count > 0:
            confidence = min(1.0, confidence + (0.05 * technical_count))
        
        return round(confidence, 2)
