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
            # Cambiado de 'gemini-1.5-flash' a 'gemini-1.5-pro' por error 404
            self.model = genai.GenerativeModel('gemini-1.5-pro')
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
Eres un experto en ciberseguridad explicando a un empleado sin conocimientos técnicos.

Contexto:
- Se analizó un {tipo}
- {positives} de {total} motores antivirus detectaron amenazas.

Tu tarea: Generar una respuesta JSON estricta con dos campos:
1. "explicacion": Una frase ÚNICA y MEMORABLE de máximo 20 palabras. Debe sonar humana, como una advertencia de una secretaria o amigo.
   - Si es MALWARE (>0 positivos): Usa tono de advertencia claro. Ej: "Secretaria: ¡Cuidado! No abras esto, es un virus peligroso."
   - Si es SEGURO (0 positivos): Usa tono tranquilo. Ej: "Todo parece estar limpio y seguro."
   
2. "recomendacion": Una acción concreta (ej: "Eliminar archivo", "Abrir con confianza").

Formato JSON esperado:
{{
  "explicacion": "...",
  "recomendacion": "..."
}}
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
