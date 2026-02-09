import requests
import hashlib
import time
import logging
from decouple import config

logger = logging.getLogger(__name__)

class MetaDefenderService:
    # Servicio para usar MetaDefender (otra opcion de antivirus)
    # Lo uso si VirusTotal falla
    
    def __init__(self):
        self.api_key = config('METADEFENDER_API_KEY', default='')
        self.base_url = 'https://api.metadefender.com/v4'
    
    def analyze_file(self, file_obj):
        # Manda el archivo a MetaDefender y devuelve resultados
        if not self.api_key:
            logger.error("[MD] Falta la clave de API")
            return {'error': 'Falta la clave de API'}
        
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
                    'source': 'MetaDefender',
                    'link': f"https://metadefender.opswat.com/results/file/{file_hash}/hash/overview"
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
                            'source': 'MetaDefender',
                            'link': f"https://metadefender.opswat.com/results/file/{data_id}/regular/overview"
                        }
            
            logger.warning("[MD] Timeout esperando análisis")
            return {'error': 'Timeout'}
            
        except Exception as e:
            logger.error(f"[MD] Error: {e}")
            return {'error': str(e)}

    def analyze_file_hash(self, file_hash):
        # Analiza un archivo por su hash (sin subirlo)
        if not self.api_key:
             return {'error': 'Falta la clave de API'}

        try:
            logger.info(f"[MD] Hash: {file_hash}")
            
            # Buscar por hash
            lookup_url = f"{self.base_url}/hash/{file_hash}"
            headers = {'apikey': self.api_key}
            
            lookup_response = requests.get(lookup_url, headers=headers, timeout=30)
            
            if lookup_response.status_code == 200:
                data = lookup_response.json()
                scan_results = data.get('scan_results', {})
                
                total_detected = scan_results.get('total_detected_avs', 0)
                total_avs = scan_results.get('total_avs', 0)
                
                return {
                    'positives': total_detected,
                    'total': total_avs,
                    'scan_date': data.get('scan_date', ''),
                    'source': 'MetaDefender',
                    'link': f"https://metadefender.opswat.com/results/file/{file_hash}/hash/overview"
                }
            else:
                 return {'error': 'Archivo no encontrado en MetaDefender'}

        except Exception as e:
             logger.error(f"[MD] Error hash: {e}")
             return {'error': str(e)}

    def analyze_url(self, url):
        # Analiza una URL
        if not self.api_key:
             return {'error': 'Falta la clave de API'}

        try:
            logger.info(f"[MD] Analizando URL: {url}")
            
            # 1. Enviar URL para escanear
            submit_url = f"{self.base_url}/url"
            headers = {'apikey': self.api_key}
            payload = {'url': url}
            
            response = requests.post(submit_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                data_id = data.get('data_id')
                
                # 2. Esperar resultados
                for attempt in range(10):
                    time.sleep(3)
                    result_url = f"{self.base_url}/url/{data_id}"
                    result_response = requests.get(result_url, headers=headers)
                    
                    if result_response.status_code == 200:
                        res_data = result_response.json()
                        scan_results = res_data.get('scan_results', {})
                        
                        if scan_results.get('progress_percentage') == 100:
                            total_detected = scan_results.get('total_detected_avs', 0)
                            total_avs = scan_results.get('total_avs', 0)
                            
                            return {
                                'positives': total_detected,
                                'total': total_avs,
                                'source': 'MetaDefender',
                                'link': f"https://metadefender.opswat.com/results/url/{data_id}/overview"
                            }
            
            logger.warning(f"[MD] No se pudo analizar URL. Status: {response.status_code}")
            return {'error': 'No se pudo iniciar analisis'}

        except Exception as e:
             logger.error(f"[MD] Error URL: {e}")
             return {'error': str(e)}
