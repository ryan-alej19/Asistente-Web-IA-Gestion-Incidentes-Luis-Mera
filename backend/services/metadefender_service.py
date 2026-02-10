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
        import urllib.parse
        # Analiza una URL
        if not self.api_key:
             return {'error': 'Falta la clave de API'}

        try:
            logger.info(f"[MD] Analizando URL: {url}")
            
            # 1. Intentar buscar analisis previo (Lookup GET)
            # Encode URL including slashes
            # Encode URL including slashes
            encoded_url = urllib.parse.quote(url, safe='')
            lookup_url = f"{self.base_url}/url/{encoded_url}"
            headers = {'apikey': self.api_key}
            
            logger.info(f"[MD] Lookup URL: {lookup_url} with Key: {self.api_key[:5]}...")
            
            try:
                # Timeout corto para lookup
                response = requests.get(lookup_url, headers=headers, timeout=10)
                logger.info(f"[MD] Lookup Status: {response.status_code}")
                
                if response.status_code == 200:
                    res_data = response.json()
                    # logger.info(f"[MD] Lookup Payload: {str(res_data)[:200]}") # Commented out to avoid noise
                    
                    scan_results = {}
                    
                    if 'scan_results' in res_data:
                         scan_results = res_data.get('scan_results', {})
                         total_detected = scan_results.get('total_detected_avs', 0)
                         total_avs = scan_results.get('total_avs', 0)
                    elif 'lookup_results' in res_data:
                         # Formato alternativo de lookup
                         lookup = res_data.get('lookup_results', {})
                         total_detected = lookup.get('detected_by', 0)
                         sources = lookup.get('sources', [])
                         total_avs = len(sources)
                    else:
                         # Si devuelve formato corto o diferente, intentamos adaptar
                         scan_results = res_data
                         total_detected = scan_results.get('total_detected_avs', 0)
                         total_avs = scan_results.get('total_avs', 0)
                    
                    # Si tiene datos validos, retornamos
                    # Aceptamos total_avs > 0 o si lookup_results existe (aunque sea 0 detected)
                    if total_avs > 0 or 'lookup_results' in res_data:
                        logger.info(f"[MD] Lookup exitoso: {total_detected}/{total_avs}")
                        return {
                            'positives': total_detected,
                            'total': total_avs,
                            'source': 'MetaDefender',
                            'link': f"https://metadefender.opswat.com/results/url/{urllib.parse.quote(url, safe='')}/overview" 
                        }
            except Exception as e:
                logger.warning(f"[MD] Error en lookup: {e}")

            # 2. Si no existe o falla lookup, intentar Enviar (SCAN)
            # Nota: Endpoint POST /url suele ser estricto o fallar. 
            # Si falla, retornamos error pero sin crashear.
            
            submit_url = f"{self.base_url}/url"
            # headers ya tiene apikey
            # Forzamos content-type correcto
            headers['Content-Type'] = 'application/json'
            payload = {'url': url}
            
            response = requests.post(submit_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                data_id = data.get('data_id')
                
                # 3. Esperar resultados (Aumentamos a 20 intentos x 3s = 60s)
                for attempt in range(20):
                    time.sleep(3)
                    result_url = f"{self.base_url}/url/{data_id}"
                    result_response = requests.get(result_url, headers=headers)
                    
                    if result_response.status_code == 200:
                        res_data = result_response.json()
                        scan_results = res_data.get('scan_results', {})
                        
                        # Si ya tiene resultados (aunque sea parcial) o progreso 100
                        if scan_results.get('progress_percentage') == 100 or 'total_detected_avs' in scan_results:
                            total_detected = scan_results.get('total_detected_avs', 0)
                            total_avs = scan_results.get('total_avs', 0)
                            
                            # Si total_avs es 0, es que aun esta encolado posiblemente, seguimos esperando un poco mas
                            if total_avs == 0 and attempt < 15:
                                continue

                            return {
                                'positives': total_detected,
                                'total': total_avs,
                                'source': 'MetaDefender',
                                'link': f"https://metadefender.opswat.com/results/url/{data_id}/overview"
                            }
            
            logger.warning(f"[MD] Timeout o error en analisis URL. Status: {response.status_code}. Msg: {response.text[:100]}")
            return {'error': 'Timeout o error'}

        except Exception as e:
             logger.error(f"[MD] Error URL: {e}")
             return {'error': str(e)}
