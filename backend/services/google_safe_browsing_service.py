import requests
import logging
from decouple import config

logger = logging.getLogger(__name__)

class GoogleSafeBrowsingService:
    """
    Servicio de Google Safe Browsing para verificar URLs.
    Usa la infraestructura de Google Cloud.
    """
    
    def __init__(self):
        # Usamos la misma Key de Gemini (Google Cloud)
        self.api_key = config('GEMINI_API_KEY', default='')
        self.api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={self.api_key}"
        
    def check_url(self, url):
        """
        Consulta si una URL es peligrosa.
        Retorna: dict con risk_level, message, detail
        """
        if not self.api_key:
            return {'error': 'API Key no configurada'}

        payload = {
            "client": {
                "clientId": "tesis-ciberseguridad",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": url}
                ]
            }
        }
        
        try:
            logger.info(f"Escaneando URL con Google Safe Browsing: {url}")
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Error Safe Browsing API: {response.status_code}")
                return {'error': f'Status {response.status_code}'}
                
            data = response.json()
            
            # Si hay "matches", es peligroso
            if 'matches' in data and len(data['matches']) > 0:
                match = data['matches'][0]
                threat_type = match.get('threatType', 'UNKNOWN')
                logger.warning(f"Google Safe Browsing DETECTO amenaza: {threat_type}")
                
                return {
                    'safe': False,
                    'risk_level': 'CRITICAL',
                    'message': 'SITIO PELIGROSO DETECTADO',
                    'detail': f'Google Safe Browsing clasificó este sitio como: {threat_type.replace("_", " ")}',
                    'source': 'Google Safe Browsing'
                }
            
            # Si no hay matches, es seguro (por ahora)
            logger.info("Google Safe Browsing: URL Limpia")
            return {
                'safe': True,
                'risk_level': 'LOW',
                'message': 'URL Verificada por Google',
                'detail': 'Google Safe Browsing no encontró amenazas actuales en este enlace.',
                'source': 'Google Safe Browsing'
            }
            
        except Exception as e:
            logger.error(f"Excepción en Safe Browsing: {e}")
            return {'error': str(e)}
