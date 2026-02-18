import requests
import hashlib
import time
import logging
from decouple import config

logger = logging.getLogger(__name__)

class VirusTotalService:
    # Servicio para analizar enlaces y archivos con VirusTotal
    # Permite buscar si ya fue analizado o subir un archivo nuevo
    
    def __init__(self):
        self.api_key = config('VIRUSTOTAL_API_KEY', default='')
        self.base_url = 'https://www.virustotal.com/vtapi/v2'
    
    def analyze_url(self, url):
        # Manda una URL a VirusTotal para ver si es segura
        # Devuelve cuantos antivirus dicen que es peligroso
        if not self.api_key:
            return {'error': 'Falta la clave de API'}
        
        try:
            # Escanear URL
            scan_url = f"{self.base_url}/url/scan"
            params = {'apikey': self.api_key, 'url': url}
            
            response = requests.post(scan_url, data=params)
            scan_data = response.json()
            
            # Obtener el reporte
            report_url = f"{self.base_url}/url/report"
            params = {'apikey': self.api_key, 'resource': url}
            
            # Espero el resultado (intento varias veces por si tarda)
            for attempt in range(12):
                time.sleep(5)
                report_response = requests.get(report_url, params=params)
                
                # Si me pase del limite de uso gratuito
                if report_response.status_code in [204, 429]:
                    logger.info(f"Se acabo la cuota gratuita de VirusTotal ({report_response.status_code}).")
                    return {'error': 'Limite excedido'}
                
                report_data = report_response.json()
                
                # Codigo 1 significa que ya termino de analizar
                if report_data.get('response_code') == 1:
                    return {
                        'positives': report_data.get('positives', 0),
                        'total': report_data.get('total', 0),
                        'permalink': report_data.get('permalink', ''),
                        'scan_date': report_data.get('scan_date', ''),
                        'link': report_data.get('permalink', ''),
                    }
                elif report_data.get('response_code') == -2:
                    logger.info(f"VirusTotal todavia esta analizando... Intento {attempt+1}")
                    continue
            
            return {'error': 'Tardo demasiado tiempo'}
            
        except Exception as e:
            logger.error(f"Error en VirusTotal: {e}")
            return {'error': str(e)}

    def analyze_file_hash(self, file_hash):
        # Analiza un archivo por su hash (sin subirlo)
        if not self.api_key:
            return {'error': 'Falta la clave de API'}

        try:
            logger.info(f"Analizando archivo con hash: {file_hash}")
            
            # Buscar por hash
            report_url = f"{self.base_url}/file/report"
            params = {'apikey': self.api_key, 'resource': file_hash}
            
            report_response = requests.get(report_url, params=params)
            report_data = report_response.json()
            
            # Si existe reporte
            if report_data.get('response_code') == 1:
                logger.info(f"Archivo ya analizado: {report_data.get('positives')}/{report_data.get('total')}")
                return {
                    'positives': report_data.get('positives', 0),
                    'total': report_data.get('total', 0),
                    'permalink': report_data.get('permalink', ''),
                    'scan_date': report_data.get('scan_date', ''),
                    'link': report_data.get('permalink', ''),
                }
            else:
                return {'error': 'Archivo no encontrado en VirusTotal (requiere subida)'}
                
        except Exception as e:
             logger.error(f"Error analizando hash VT: {e}")
             return {'error': str(e)}
    
    def analyze_file(self, file_obj, known_hash=None):
        # Analiza un archivo
        # Primero reviso si ya existe por su hash, sino lo subo
        if not self.api_key:
            return {'error': 'Falta la clave de API'}
        
        try:
            # Calcular hash SHA-256 si no se provee
            if known_hash:
                file_hash = known_hash
            else:
                file_obj.seek(0)
                sha256_hash = hashlib.sha256()
                if hasattr(file_obj, 'chunks'):
                    for chunk in file_obj.chunks():
                        sha256_hash.update(chunk)
                else:
                    sha256_hash.update(file_obj.read())
                file_hash = sha256_hash.hexdigest()
            
            logger.info(f"Analizando archivo con hash: {file_hash}")
            
            # Buscar por hash
            report_url = f"{self.base_url}/file/report"
            params = {'apikey': self.api_key, 'resource': file_hash}
            
            report_response = requests.get(report_url, params=params)
            report_data = report_response.json()
            
            # Si existe reporte
            if report_data.get('response_code') == 1:
                logger.info(f"Archivo ya analizado: {report_data.get('positives')}/{report_data.get('total')}")
                return {
                    'positives': report_data.get('positives', 0),
                    'total': report_data.get('total', 0),
                    'permalink': report_data.get('permalink', ''),
                    'scan_date': report_data.get('scan_date', ''),
                }
            
            # Si no existe, subir archivo
            logger.info("Archivo no encontrado, subiendo...")
            file_obj.seek(0)
            
            scan_url = f"{self.base_url}/file/scan"
            files = {'file': (file_obj.name, file_obj)}
            params = {'apikey': self.api_key}
            
            scan_response = requests.post(scan_url, files=files, params=params)
            
            # Esperar analisis (max 90 seg, 18 intentos)
            for attempt in range(18):
                time.sleep(5)
                report_response = requests.get(report_url, params={'apikey': self.api_key, 'resource': file_hash})
                
                # Manejo explícito de Cuota Excedida
                if report_response.status_code in [204, 429]:
                    logger.info(f"Límite de cuota VirusTotal alcanzado ({report_response.status_code}).")
                    return {'error': 'Quota Exceeded'}
                
                if report_response.status_code == 200:
                    try:
                        report_data = report_response.json()
                        
                        # Check response_code. -2 is Queued/Scanning in V2 API
                        code = report_data.get('response_code')
                        
                        if code == 1:
                            logger.info(f"Analisis completo: {report_data.get('positives')}/{report_data.get('total')}")
                            return {
                                'positives': report_data.get('positives', 0),
                                'total': report_data.get('total', 0),
                                'permalink': report_data.get('permalink', ''),
                                'scan_date': report_data.get('scan_date', ''),
                                'link': report_data.get('permalink', ''),
                            }
                        elif code == -2:
                             logger.info(f"VirusTotal analizando archivo... Intento {attempt+1}")
                             continue
                    except ValueError:
                         continue # Json error, retry
            
            return {'error': 'Timeout esperando analisis (Scanning loop)'}
            
        except Exception as e:
            logger.error(f"Error analizando archivo: {e}")
            return {'error': str(e)}
