import logging
from decouple import config
import json
import requests
import os

logger = logging.getLogger(__name__)

class GeminiService:
    _initialized = False

    def __init__(self):
        self.api_key = config('GEMINI_API_KEY', default='')
        
        if not self.api_key:
            logger.warning("Clave API de Gemini no configurada")
            self.available = False
        else:
            self.available = True
            if not GeminiService._initialized:
                logger.info("Servicio de Inteligencia Artificial inicializado")
                GeminiService._initialized = True
    
    def explain_threat(self, positives, total, incident_type, resource_name="Desconocido"):
        if not self.available:
            return self._fallback_explanation(positives, total, incident_type)
        
        try:
            tipo = "archivo" if incident_type == "file" else "enlace web"
            porcentaje = round((positives / total * 100), 1) if total > 0 else 0
            
            # Determinar nivel de riesgo
            if positives > 50:
                nivel = "CRITICO"
            elif positives > 15:
                nivel = "ALTO"
            elif positives > 5:
                nivel = "MEDIO"
            elif positives > 0:
                nivel = "BAJO"
            else:
                nivel = "SEGURO"
            
            prompt = f"""Actúa como un Analista de Ciberseguridad Profesional. Analiza el siguiente recurso: '{resource_name}'

CONTEXTO TÉCNICO:
- Tipo: {tipo.upper()}
- Detecciones: {positives} de {total} motores de seguridad lo marcan como malicioso.
- Nivel de Riesgo Calculado: {nivel} ({porcentaje}%)

INSTRUCCIONES DE ANÁLISIS (Sigue este orden lógico):

1. VALIDACIÓN DE INPUT (Crucial):
   - Si el recurso '{resource_name}' NO es una URL válida, dirección IP, dominio o nombre de archivo técnico (ej: es un saludo como "hola", letras al azar "asdf", o nombres propios), DEBES responder que el input no es válido para análisis de seguridad.
   - NO inventes amenazas sobre texto basura.

2. WHITELISTING (Sitios Conocidos):
   - Si es un dominio oficial y legítimo (ej: google.com, facebook.com, microsoft.com), confírmalo inmediatamente como SEGURO, independientemente de falsos positivos menores.

3. ANÁLISIS DE AMENAZAS:
   - Si es un archivo comprimido (.zip, .rar, .7z) y tiene POCAS detecciones (0-2), DEBES ADVERTIR que el contenido podría estar cifrado con contraseña y ocultar malware. Recomienda NO abrir si no se confía en el origen.
   - Si es un recurso válido y desconocido, basa tu veredicto en las {positives} detecciones.
   - Explica técnicamente qué implica (Phishing, Malware, etc.) si hay detecciones.

FORMATO DE RESPUESTA (JSON PURO):
{{
    "explicacion": "Análisis profesional y objetivo (2-3 frases). Si el input es inválido, indícalo. Si es un sitio conocido, confírmalo.",
    "recomendacion": "Acción recomendada. Ej: 'Navegar con confianza', 'Bloquear acceso', 'Ingresar una URL válida'."
}}

Responde ÚNICAMENTE con el objeto JSON válido."""
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 2048
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Error en API de Gemini: {response.status_code}")
                return self._fallback_explanation(positives, total, incident_type)
            
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Limpiar markdown
            text = text.replace('```json', '').replace('```', '').strip()
            if text.startswith('json'):
                text = text[4:].strip()
            
            # Intentar parsear JSON
            try:
                result = json.loads(text)
            except json.JSONDecodeError as e:
                logger.error(f"[GEMINI] Error JSON: {e} - Texo recibido: {text[:50]}...")
                # Intento de corrección simple (si faltan llaves)
                if '{' in text and '}' not in text:
                    text += '"}' # Intento desesperado de cerrar el string y el JSON
                    try: result = json.loads(text)
                    except: return self._fallback_explanation(positives, total, incident_type)
                else:
                    return self._fallback_explanation(positives, total, incident_type)
            
            if len(result.get('explicacion', '')) < 30: # Bajamos umbral, a veces explicaciones cortas son validas
                 logger.warning("[GEMINI] Explicacion muy corta, usando fallback")
                 return self._fallback_explanation(positives, total, incident_type)
            
            logger.info("[GEMINI] Analisis generado correctamente")
            return result
            
        except Exception as e:
            logger.error(f"[GEMINI] Error General en explain_threat: {str(e)}")
            return self._fallback_explanation(positives, total, incident_type)
    
    def _fallback_explanation(self, positives, total, incident_type='file'):
        """Explicaciones de respaldo cuando Gemini falla"""
        item_name = "este archivo" if incident_type == 'file' else "este enlace web"
        action_name = "abrirlo" if incident_type == 'file' else "visitarlo"
        
        if positives > 50:
            return {
                'explicacion': f'{item_name.capitalize()} fue identificado como muy peligroso por {positives} empresas de seguridad. Puede robar informacion o dañar el sistema.',
                'recomendacion': f'NO intente {action_name}. Reportelo inmediatamente.'
            }
        elif positives > 15:
            return {
                'explicacion': f'{item_name.capitalize()} fue marcado como peligroso por {positives} de {total} motores. Es muy probable que sea malicioso.',
                'recomendacion': f'NO {action_name}. Eliminelo o cierre la ventana.'
            }
        elif positives > 5:
            return {
                'explicacion': f'{item_name.capitalize()} levanto alertas en {positives} sistemas. Podria ser riesgoso.',
                'recomendacion': f'Evite {action_name} si no confia en la fuente.'
            }
        elif positives > 0:
            return {
                'explicacion': f'{item_name.capitalize()} tiene caracteristicas sospechosas para {positives} motores, aunque la mayoria lo considera seguro.',
                'recomendacion': 'Proceda con precaucion.'
            }
        else:
            return {
                'explicacion': f'{item_name.capitalize()} fue revisado por {total} empresas de seguridad y ninguna encontro amenazas.',
                'recomendacion': f'Es seguro {action_name}.'
            }

    def analyze_image(self, file_bytes, mime_type="image/jpeg"):
        if not self.available:
            return {
                "explicacion": "Análisis inteligente no disponible por falta de API Key.",
                "recomendacion": "Por favor revisa la imagen manualmente."
            }
            
        import base64
        encoded_image = base64.b64encode(file_bytes).decode('utf-8')

        prompt = """Actúa como un Analista de Ciberseguridad Experto especializado en visión artificial y OCR. Analiza la siguiente captura de pantalla o imagen proporcionada por un empleado.

OBJETIVO:
El usuario ha subido esta imagen porque sospecha que podría ser un intento de ciberataque, phishing, estafa, extorsión, o malware.

INSTRUCCIONES DE ANÁLISIS:
1. Inspecciona la imagen detenidamente en busca de señales de fraude (ej: correos falsos simulando ser un banco, mensajes de WhatsApp sospechosos, ventanas emergentes de "virus detectado", enlaces extraños, faltas de ortografía, urgencia o amenazas).
2. EXTRAE TEXTO (OCR): Si logras leer alguna URL, dominio web, o enlace dentro de la imagen (ejemplo: 'http://hacker.com', 'banco-falso.net', 'bit.ly/123'), extráelo y colócalo en el arreglo 'urls_extraidas'. Si no hay ninguna URL visible, devuelve un arreglo vacío [].
3. Si la imagen NO contiene nada sospechoso y es completamente inofensiva (ejemplo: la foto de un perrito, un paisaje, un documento normal), clasifícala como "SEGURO" e indícale al usuario de forma clara pero profesional qué es lo que ves en la imagen para tranquilizarlo.
4. ESTRICTAMENTE define el Nivel de Riesgo usando exactamente una de estas palabras: CRÍTICO, ALTO, MEDIO, BAJO, o SEGURO.

FORMATO DE RESPUESTA (JSON PURO):
{
    "riesgo": "Nivel detectado (CRÍTICO, ALTO, MEDIO, BAJO, o SEGURO)",
    "explicacion": "Análisis profesional del contenido de la imagen (2-3 frases), justificando por qué es peligroso o inofensivo. Si es algo normal como un perro o paisaje, menciónalo.",
    "recomendacion": "Acción inmediata recomendada.",
    "urls_extraidas": ["ejemplo.com", "http://malicioso.net/login"]
}

Responde ÚNICAMENTE con el objeto JSON válido, sin bloques de código ni texto adicional."""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.api_key}"
            
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": encoded_image
                        }
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048
            }
        }
            
        try:
            response = requests.post(url, json=payload, timeout=45)
            
            if response.status_code != 200:
                logger.error(f"Error en API de Gemini Imagen: {response.status_code} - {response.text}")
                return {
                    "riesgo": "MEDIO",
                    "explicacion": "El motor de Inteligencia Artificial falló al analizar la imagen.",
                    "recomendacion": "Por favor revisar manualmente."
                }
            
            data = response.json()
            text = data['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Limpiar markdown
            text = text.replace('```json', '').replace('```', '').strip()
            if text.startswith('json'):
                text = text[4:].strip()
            
            return json.loads(text)
            
        except Exception as e:
            logger.error(f"Error procesando imagen con Gemini: {e}")
            return {
                "riesgo": "MEDIO",
                "explicacion": "Ocurrió un error inesperado al procesar la imagen con el servicio de Inteligencia Artificial.",
                "recomendacion": "Contactar a soporte técnico o revisar manualmente."
            }
