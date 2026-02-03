import google.generativeai as genai
import logging
from decouple import config
import json

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Servicio de análisis con Google Gemini.
    Traduce resultados técnicos a lenguaje simple.
    """
    
    def __init__(self):
        api_key = config('GEMINI_API_KEY', default='')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("Gemini API key no configurada")
    
    def explain_threat(self, positives, total, incident_type):
        """
        Genera explicación simple del análisis.
        
        Args:
            positives: Número de detectores que encontraron amenazas
            total: Total de detectores
            incident_type: 'file' o 'url'
        
        Returns:
            dict con explicacion y recomendacion
        """
        if not self.model:
            return self._fallback_explanation(positives, total)
        
        try:
            tipo = "archivo" if incident_type == "file" else "enlace"
            
            prompt = f"""
Eres un asistente de seguridad que explica a empleados de oficina.

Contexto:
- Se analizó un {tipo}
- {positives} de {total} antivirus detectaron que es peligroso

Genera una respuesta en JSON con este formato:
{{
  "explicacion": "Explicación simple de 15-20 palabras sobre qué significa esto",
  "recomendacion": "Una acción clara que el empleado debe hacer"
}}

Reglas:
- Sin términos técnicos (malware, exploit, payload)
- Como si explicaras a tu abuela
- Directo y claro
- En español
"""
            
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Limpiar respuesta
            text = text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(text)
            
            logger.info(f"Gemini: {result.get('explicacion')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error con Gemini: {e}")
            return self._fallback_explanation(positives, total)
    
    def _fallback_explanation(self, positives, total):
        """
        Explicación de respaldo si Gemini falla.
        """
        if positives > 15:
            return {
                'explicacion': 'Este archivo contiene un virus peligroso que puede dañar la computadora',
                'recomendacion': 'No lo abras. Reporta este incidente inmediatamente al administrador.'
            }
        elif positives > 5:
            return {
                'explicacion': 'Varios antivirus detectaron que este archivo es sospechoso',
                'recomendacion': 'No lo abras hasta que el equipo de seguridad lo revise.'
            }
        elif positives > 0:
            return {
                'explicacion': 'Algunos antivirus marcaron este archivo como potencialmente riesgoso',
                'recomendacion': 'Consulta con el equipo de seguridad antes de abrirlo.'
            }
        else:
            return {
                'explicacion': f'El archivo fue revisado por {total} antivirus y no encontraron amenazas',
                'recomendacion': 'Es seguro usar este archivo normalmente.'
            }
