import requests
import hashlib
import time
import logging
from decouple import config

logger = logging.getLogger(__name__)

class VirusTotalService:
    """
    Servicio para analizar URLs y archivos con VirusTotal API v2.
    Maneja busqueda por hash y subida de archivos nuevos.
    """
    
    def __init__(self):
        self.api_key = config('VIRUSTOTAL_API_KEY', default='')
        self.base_url = 'https://www.virustotal.com/vtapi/v2'
    
    def analyze_url(self, url):
        """
        Analiza una URL con VirusTotal.
        Retorna diccionario con positives, total, y permalink.
        """
        if not self.api_key:
            return {'error': 'API key no configurada'}
        
        try:
            # Escanear URL
            scan_url = f"{self.base_url}/url/scan"
            params = {'apikey': self.api_key, 'url': url}
            
            response = requests.post(scan_url, data=params)
            scan_data = response.json()
            
            # Obtener reporte
            report_url = f"{self.base_url}/url/report"
            params = {'apikey': self.api_key, 'resource': url}
            
            # Esperar resultado (max 30 seg)
            for attempt in range(6):
                time.sleep(5)
                report_response = requests.get(report_url, params=params)
                report_data = report_response.json()
                
                if report_data.get('response_code') == 1:
                    return {
                        'positives': report_data.get('positives', 0),
                        'total': report_data.get('total', 0),
                        'permalink': report_data.get('permalink', ''),
                        'scan_date': report_data.get('scan_date', ''),
                    }
            
            return {'error': 'Timeout esperando resultado'}
            
        except Exception as e:
            logger.error(f"Error en VirusTotal: {e}")
            return {'error': str(e)}
    
    def analyze_file(self, file_obj):
        """
        Analiza un archivo con VirusTotal.
        Primero busca por hash, si no existe lo sube.
        """
        if not self.api_key:
            return {'error': 'API key no configurada'}
        
        try:
            # Calcular hash SHA-256
            file_obj.seek(0)
            sha256_hash = hashlib.sha256()
            for chunk in file_obj.chunks():
                sha256_hash.update(chunk)
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
            
            # Esperar analisis (max 60 seg)
            for attempt in range(12):
                time.sleep(5)
                report_response = requests.get(report_url, params={'apikey': self.api_key, 'resource': file_hash})
                report_data = report_response.json()
                
                if report_data.get('response_code') == 1:
                    logger.info(f"Analisis completo: {report_data.get('positives')}/{report_data.get('total')}")
                    return {
                        'positives': report_data.get('positives', 0),
                        'total': report_data.get('total', 0),
                        'permalink': report_data.get('permalink', ''),
                        'scan_date': report_data.get('scan_date', ''),
                    }
            
            return {'error': 'Timeout esperando analisis'}
            
        except Exception as e:
            logger.error(f"Error analizando archivo: {e}")
            return {'error': str(e)}
