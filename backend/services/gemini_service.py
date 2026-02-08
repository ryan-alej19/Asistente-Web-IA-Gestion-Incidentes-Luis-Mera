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
        if not self.api_key:
            return self._fallback_explanation(positives, total)
        
        try:
            tipo = "archivo" if incident_type == "file" else "enlace web"
            porcentaje = round((positives / total * 100), 1) if total > 0 else 0
            
            # Contexto más específico
            if positives > 50:
                contexto = f"MUY PELIGROSO: {positives} de {total} antivirus profesionales (empresas como Microsoft, Kaspersky, Norton) detectaron este {tipo} como malware"
            elif positives > 15:
                contexto = f"PELIGROSO: {positives} de {total} antivirus profesionales detectaron amenazas en este {tipo}"
            elif positives > 5:
                contexto = f"SOSPECHOSO: {positives} de {total} antivirus alertaron sobre este {tipo}"
            elif positives > 0:
                contexto = f"PRECAUCIÓN: {positives} de {total} antivirus tienen dudas sobre este {tipo}"
            else:
                contexto = f"SEGURO: Los {total} antivirus profesionales revisaron este {tipo} y NO encontraron nada malo"
            
            prompt = f"""Eres un analista de ciberseguridad senior del CSIRT ecuatoriano explicando a personal administrativo de una PYME.

CONTEXTO:
{contexto}

SITUACIÓN:
Una secretaria de 45 años, sin conocimientos técnicos, acaba de recibir este {tipo} por correo y está a punto de abrirlo. Ella NO entiende términos como "malware", "exploit", "ransomware", "phishing".

TU TRABAJO:
Explicarle en 2-3 oraciones CONCRETAS qué es esta amenaza y qué puede pasar si lo abre.

EJEMPLOS DE EXPLICACIONES BUENAS:

Para archivo PELIGROSO:
"Este archivo contiene un programa malicioso que puede robar sus contraseñas del banco, bloquear todos los archivos de la computadora pidiendo un rescate en dinero, o permitir que delincuentes vean todo lo que hace en su computadora."

Para archivo SOSPECHOSO:
"Este archivo tiene características que varios antivirus consideran riesgosas. Podría intentar instalar programas no deseados o modificar configuraciones importantes de la computadora sin su permiso."

Para archivo SEGURO:
"Este archivo fue revisado por {total} empresas de seguridad profesionales (como las que protegen bancos y hospitales) y ninguna encontró programas maliciosos. Es seguro abrirlo."

EJEMPLOS DE EXPLICACIONES MALAS (NO HAGAS ESTO):
❌ "El archivo es altamente sospechoso y probablemente malicioso"
❌ "Presenta características de malware"
❌ "Se recomienda precaución"

RECOMENDACIONES BUENAS:

Para PELIGROSO:
"NO abra este archivo bajo ninguna circunstancia. Elimínelo inmediatamente de su correo y de la papelera. Avise al encargado de sistemas que recibió un archivo peligroso."

Para SOSPECHOSO:
"NO abra este archivo todavía. Reenvíelo al encargado de sistemas o al administrador para que lo revise con herramientas especializadas antes de abrirlo."

Para SEGURO:
"Puede abrir este archivo con tranquilidad. Fue verificado por múltiples sistemas de seguridad profesionales."

RECOMENDACIONES MALAS (NO HAGAS ESTO):
❌ "Borrar"
❌ "Tener precaución"
❌ "Consultar con TI"

AHORA GENERA TU RESPUESTA EN JSON:
{{
  "explicacion": "2-3 oraciones CONCRETAS explicando qué es y qué puede hacer",
  "recomendacion": "Instrucción ESPECÍFICA y ACCIONABLE de qué hacer paso por paso"
}}

GENERA LA RESPUESTA:"""
            
            # Lista de modelos (Prioridad 2026)
            models_to_try = [
                "gemini-2.0-flash",
                "gemini-1.5-flash",
            ]
            
            headers = { 'Content-Type': 'application/json' }
            payload = {
                "contents": [{ "parts": [{"text": prompt}] }],
                "generationConfig": { 
                    "responseMimeType": "application/json",
                    "temperature": 0.7,
                    "maxOutputTokens": 400
                }
            }

            for model_name in models_to_try:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.api_key}"
                    logger.info(f"🔄 [GEMINI] Probando: {model_name}...")
                    
                    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        text_response = data['candidates'][0]['content']['parts'][0]['text']
                        result = json.loads(text_response)
                        
                        # VALIDACIÓN ESTRICTA
                        explicacion = result.get('explicacion', '').strip()
                        recomendacion = result.get('recomendacion', '').strip()
                        
                        if len(explicacion) < 30:
                             logger.warning(f"[GEMINI] Explicación corta: {explicacion}")
                        
                        logger.info(f"✅ [GEMINI] Éxito con {model_name}")
                        return result
                    else:
                        logger.warning(f"⚠️ Falló {model_name}: {response.status_code}")
                        continue
                except Exception as e:
                    logger.error(f"❌ Error conexión {model_name}: {e}")
                    continue

            logger.error("[GEMINI] Todos los modelos fallaron.")
            return self._fallback_explanation(positives, total)
            
        except Exception as e:
            logger.error(f"[GEMINI] Error general: {str(e)}")
            return self._fallback_explanation(positives, total)

    def _fallback_explanation(self, positives, total):
        """
        Explicaciones de respaldo DETALLADAS (no genéricas).
        """
        if positives > 50:
            return {
                'explicacion': f'Este archivo fue identificado como muy peligroso por {positives} empresas de seguridad profesionales. Contiene programas maliciosos que pueden robar información personal, contraseñas bancarias, o bloquear todos los archivos de la computadora exigiendo un pago.',
                'recomendacion': 'NO abra este archivo bajo ninguna circunstancia. Elimínelo inmediatamente del correo y de la papelera de reciclaje. Avise al encargado de sistemas que recibió un archivo peligroso por correo.'
            }
        elif positives > 15:
            return {
                'explicacion': f'Este archivo fue marcado como peligroso por {positives} de {total} antivirus profesionales. Puede contener programas que roban información, instalan virus, o permiten que personas externas accedan a la computadora sin permiso.',
                'recomendacion': 'NO abra este archivo. Elimínelo de su correo inmediatamente y avise al administrador de sistemas o al encargado de tecnología de su empresa.'
            }
        elif positives > 5:
            return {
                'explicacion': f'Este archivo levantó alertas en {positives} sistemas de seguridad. Podría intentar modificar configuraciones de la computadora, instalar programas no deseados, o acceder a información sin su permiso.',
                'recomendacion': 'NO abra este archivo todavía. Reenvíelo al encargado de sistemas para que lo revise con herramientas especializadas antes de abrirlo.'
            }
        elif positives > 0:
            return {
                'explicacion': f'Este archivo tiene algunas características que {positives} antivirus consideran sospechosas, aunque la mayoría ({total - positives}) no encontró problemas graves.',
                'recomendacion': 'Por precaución, consulte con el encargado de sistemas antes de abrir este archivo, especialmente si no estaba esperándolo o viene de un remitente desconocido.'
            }
        else:
            return {
                'explicacion': f'Este archivo fue revisado por {total} empresas de seguridad profesionales (las mismas que protegen bancos, hospitales y gobiernos) y ninguna encontró programas maliciosos o peligrosos.',
                'recomendacion': 'Puede abrir este archivo con tranquilidad. Fue verificado exhaustivamente y es seguro.'
            }
