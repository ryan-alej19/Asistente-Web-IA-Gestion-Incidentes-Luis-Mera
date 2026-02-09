import requests
import logging
from decouple import config

logger = logging.getLogger(__name__)

class GoogleSafeBrowsingService:
    # Servicio de Google para revisar si una pagina web es peligrosa
    # Funciona igual que cuando Chrome te avisa de un sitio rojo
    
    def __init__(self):
        # Usar clave especifica o fallback a Gemini
        self.api_key = config('GOOGLE_SAFE_BROWSING_API_KEY', default='')
        self.api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.api_key}"
        
    def check_url(self, url):
        if not self.api_key:
            # Si no hay API Key, se considera seguro por defecto, pero se añade una nota.
            logger.warning("Google Safe Browsing API Key no configurada. Saltando verificación.")
            return {'safe': True, 'note': 'No API Key'}

        try:
            payload = {
                "client": {
                    "clientId": "tesis-asistente",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [
                        {"url": url}
                    ]
                }
            }
            
            logger.info(f"Escaneando URL con Google Safe Browsing: {url}")
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"[GSB] API Error: {response.status_code} - {response.text}")
                # Fallback seguro si falla la API, pero se indica el error para debugging
                return {'safe': True, 'error': f'GSB API Status {response.status_code}'}
                
            data = response.json()
            matches = data.get('matches', [])
            
            if matches:
                threat_type = matches[0].get('threatType', 'UNKNOWN')
                logger.warning(f"Google Safe Browsing DETECTO amenaza para {url}: {threat_type}")
                return {
                    'safe': False,
                    'risk_level': 'CRITICAL',
                    'message': 'SITIO PELIGROSO DETECTADO',
                    'detail': f'Google Safe Browsing clasificó este sitio como: {threat_type.replace("_", " ")}',
                    'source': 'Google Safe Browsing',
                    'link': f'https://transparencyreport.google.com/safe-browsing/search?url={url}'
                }
            
            # Si no hay matches, es seguro (por ahora)
            logger.info("Google Safe Browsing: URL Limpia")
            return {
                'safe': True,
                'risk_level': 'LOW',
                'message': 'URL Verificada por Google',
                'detail': 'Google Safe Browsing no encontró amenazas actuales en este enlace.',
                'source': 'Google Safe Browsing',
                'link': f'https://transparencyreport.google.com/safe-browsing/search?url={url}'
            }
            
        except Exception as e:
            logger.error(f"Excepción en Safe Browsing: {e}")
            return {'error': str(e)}
