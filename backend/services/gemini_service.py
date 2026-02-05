import requests
import json
import os
import logging
from decouple import config

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Servicio de análisis con Google Gemini (Estrategia 2026).
    Usa API REST directa y modelos Serie 2.0 para evitar 404s.
    """
    
    def __init__(self):
        self.api_key = config('GEMINI_API_KEY', default='')
        if not self.api_key:
             self.api_key = os.getenv('GEMINI_API_KEY')

    def explain_threat(self, positives, total, incident_type):
        """
        Genera explicación iterando sobre modelos 2.0 y 1.5.
        """
        if not self.api_key:
            return self._fallback_explanation(positives, total)

        # 1. Definimos el Prompt (JSON estricto)
        tipo = "archivo" if incident_type == "file" else "enlace"
        prompt = f"""Eres un asistente de seguridad.
Contexto: Se analizó un {tipo} y {positives} de {total} antivirus detectaron amenazas.

Tu tarea: Generar un JSON con este formato exacto:
{{
  "explicacion": "Resumen de riesgo en 1 frase sencilla (español)",
  "recomendacion": "Acción recomendada (Borrar/No abrir)"
}}"""

        # 2. Lista de Modelos (SOLICITUD USUARIO: Prioridad Gemini 2.0 Flash)
        models_to_try = [
            "gemini-2.0-flash",         # <--- PRIORIDAD ABSOLUTA (Estándar 2026)
            "gemini-1.5-flash",         # Fallback por seguridad
        ]
        
        headers = { 'Content-Type': 'application/json' }
        payload = {
            "contents": [{ "parts": [{"text": prompt}] }],
            "generationConfig": { "responseMimeType": "application/json" }
        }

        # 3. Bucle de Intentos
        for model_name in models_to_try:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                
                logger.info(f"🔄 [GEMINI] Probando: {model_name}...")
                
                response = requests.post(
                    url, 
                    headers=headers, 
                    data=json.dumps(payload),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    text_response = data['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parsear JSON
                    result = json.loads(text_response)
                    logger.info(f"✅ [GEMINI] Éxito con {model_name}")
                    return result
                else:
                    logger.warning(f"⚠️ Falló {model_name}: {response.status_code}")
                    continue

            except Exception as e:
                logger.error(f"❌ Error conexión {model_name}: {e}")
                continue

        # Si todo falla
        logger.error("[GEMINI] Todos los modelos fallaron.")
        return self._fallback_explanation(positives, total)

    def _fallback_explanation(self, positives, total):
        """Fallback estático si la IA falla."""
        msg_risk = "Alto riesgo detectado" if positives > 0 else "Archivo limpio"
        msg_action = "No abrir y borrar" if positives > 0 else "Uso seguro"
        
        if positives > 5:
            msg_risk = "Amenaza crítica confirmada por múltiples motores"
            msg_action = "Eliminar inmediatamente y reportar"
            
        return {
            "explicacion": msg_risk,
            "recomendacion": msg_action
        }
