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
            # Usamos 'gemini-1.5-pro' que es el modelo flagship actual estable
            # Si la librería es muy vieja, el fallback será 'gemini-pro'
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                self.model_name = 'gemini-1.5-pro'
            except:
                logger.warning("Modelo 1.5 no encontrado, usando versión legacy estable")
                self.model = genai.GenerativeModel('gemini-pro')
                self.model_name = 'gemini-pro'
        else:
            self.model = None
            logger.warning("Gemini API key no configurada")
    
    def explain_threat(self, positives, total, incident_type):
        """
        Genera explicación simple del análisis.
        """
        if not self.model:
            return self._fallback_explanation(positives, total)
        
        try:
            tipo = "archivo" if incident_type == "file" else "enlace"
            
            prompt = f"""
Actúa como un Analista Senior de Ciberseguridad del CSIRT (Equipo de Respuesta a Incidentes). 
Tu audiencia es un empleado no técnico (secretaria/administrativo). 

Analiza los siguientes datos técnicos:
- Tipo de incidencia: {tipo}
- Motores de detección positivos: {positives} de {total}

Dame UN SOLO PÁRRAFO de advertencia clara, explicando el riesgo real (robo de datos, daño al PC, ransomware) y la acción inmediata a tomar (Borrar/No abrir). 

Tono: Urgente pero profesional. No uses tecnicismos complejos innecesarios.

Formato JSON esperado:
{{
  "explicacion": "Texto de la advertencia (Max 30 palabras)",
  "recomendacion": "Accion concreta (Ej: Borrar ahora)"
}}
"""
            
            try:
                response = self.model.generate_content(prompt)
                text = response.text.strip()
                
                # Limpiamos el texto
                text = text.replace('```json', '').replace('```', '').strip()
                result = json.loads(text)
                
                logger.info(f"Gemini ({self.model_name}) respondio: {result.get('explicacion')}")
                return result

            except Exception as e:
                logger.warning(f"Fallo modelo {self.model_name}: {e}. Intentando fallback a gemini-pro...")
                
                # Fallback a modelo Legacy si falla el Pro
                secondary_model = genai.GenerativeModel('gemini-pro')
                response = secondary_model.generate_content(prompt)
                text = response.text.strip().replace('```json', '').replace('```', '').strip()
                result = json.loads(text)
                
                logger.info(f"Gemini (Legacy) respondio: {result.get('explicacion')}")
                return result
            
        except Exception as e:
            logger.error(f"Error critico Gemini (Todos los modelos): {e}")
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
