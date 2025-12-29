"""
Tests unitarios para el clasificador de incidentes
"""

from django.test import TestCase
from .classifier import IncidentClassifier


class IncidentClassifierTests(TestCase):
    """Tests para validar clasificación de incidentes"""
    
    def setUp(self):
        self.classifier = IncidentClassifier()
    
    def test_phishing_detection(self):
        """Test: Debe detectar phishing"""
        description = "Recibí un email pidiendo que haga click para verificar mi cuenta"
        severity, confidence = self.classifier.classify(description, 'phishing')
        
        self.assertIn(severity, ['MEDIO', 'ALTO', 'CRÍTICO'])
        self.assertGreater(confidence, 0.5)
    
    def test_malware_detection(self):
        """Test: Debe detectar malware"""
        description = "Descargué un archivo que parece un virus ransomware"
        severity, confidence = self.classifier.classify(description, 'malware')
        
        self.assertEqual(severity, 'ALTO')
        self.assertGreater(confidence, 0.7)
    
    def test_suspicious_access_detection(self):
        """Test: Debe detectar acceso sospechoso"""
        description = "Alguien accedió desde una IP desconocida a horas inusuales"
        severity, confidence = self.classifier.classify(description, 'acceso_sospechoso')
        
        self.assertIn(severity, ['MEDIO', 'ALTO'])
        self.assertGreater(confidence, 0.6)
    
    def test_low_severity_with_no_keywords(self):
        """Test: Sin palabras clave = BAJO"""
        description = "El sistema está lento"
        severity, confidence = self.classifier.classify(description, 'phishing')
        
        self.assertEqual(severity, 'BAJO')
        self.assertLess(confidence, 0.5)
    
    def test_empty_description(self):
        """Test: Descripción vacía = BAJO"""
        severity, confidence = self.classifier.classify('', 'phishing')
        
        self.assertEqual(severity, 'BAJO')
    
    def test_explain_functionality(self):
        """Test: Explicación funciona"""
        description = "Email falso pidiendo contraseña"
        explanation = self.classifier.explain(description, 'phishing')
        
        self.assertIn('matched_keywords', explanation)
        self.assertGreater(explanation['total_matches'], 0)
