import requests
import hashlib
import time
import logging
from decouple import config

logger = logging.getLogger(__name__)

class MetaDefenderService:
    """
    Servicio para analizar archivos con MetaDefender (OPSWAT).
    Usado como respaldo cuando VirusTotal falla.
    """
    
    def __init__(self):
        self.api_key = config('METADEFENDER_API_KEY', default='')
        self.base_url = 'https://api.metadefender.com/v4'
    
    def analyze_file(self, file_obj):
        """
        Analiza archivo con MetaDefender.
        Retorna diccionario con positives, total.
        """
        if not self.api_key:
            logger.error("[MD] API key no configurada")
            return {'error': 'API key no configurada'}
        
        try:
            # Calcular hash SHA-256
            sha256_hash = hashlib.sha256()
            file_obj.seek(0)
            
            for chunk in file_obj.chunks():
                sha256_hash.update(chunk)
            
            file_hash = sha256_hash.hexdigest()
            
            logger.info(f"[MD] Hash: {file_hash}")
            
            # Buscar por hash
            lookup_url = f"{self.base_url}/hash/{file_hash}"
            headers = {'apikey': self.api_key}
            
            lookup_response = requests.get(lookup_url, headers=headers, timeout=30)
            
            # Si existe reporte
            if lookup_response.status_code == 200:
                data = lookup_response.json()
                scan_results = data.get('scan_results', {})
                
                total_detected = scan_results.get('total_detected_avs', 0)
                total_avs = scan_results.get('total_avs', 0)
                
                logger.info(f"[MD] Resultado existente: {total_detected}/{total_avs}")
                
                return {
                    'positives': total_detected,
                    'total': total_avs,
                    'scan_date': data.get('scan_date', ''),
                    'source': 'MetaDefender'
                }
            
            # Si no existe, subir archivo
            logger.info("[MD] Archivo no encontrado, subiendo...")
            
            file_obj.seek(0)
            
            upload_url = f"{self.base_url}/file"
            files = {'file': file_obj.read()}
            
            upload_response = requests.post(upload_url, files=files, headers=headers, timeout=60)
            upload_data = upload_response.json()
            
            data_id = upload_data.get('data_id')
            
            logger.info(f"[MD] Archivo subido, data_id: {data_id}")
            
            # Esperar análisis (máximo 60 segundos)
            for attempt in range(12):
                logger.info(f"[MD] Intento {attempt + 1}/12")
                time.sleep(5)
                
                result_url = f"{self.base_url}/file/{data_id}"
                result_response = requests.get(result_url, headers=headers, timeout=30)
                
                if result_response.status_code == 200:
                    data = result_response.json()
                    scan_results = data.get('scan_results', {})
                    
                    progress = scan_results.get('progress_percentage', 0)
                    
                    if progress == 100:
                        total_detected = scan_results.get('total_detected_avs', 0)
                        total_avs = scan_results.get('total_avs', 0)
                        
                        logger.info(f"[MD] Análisis completo: {total_detected}/{total_avs}")
                        
                        return {
                            'positives': total_detected,
                            'total': total_avs,
                            'source': 'MetaDefender'
                        }
            
            logger.warning("[MD] Timeout esperando análisis")
            return {'error': 'Timeout'}
            
        except Exception as e:
            logger.error(f"[MD] Error: {e}")
            return {'error': str(e)}
