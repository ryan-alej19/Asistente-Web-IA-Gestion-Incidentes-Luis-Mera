import sys
import os
import requests
import time
import logging

# Configure logging to stdout - DISABLED
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
# Mock logger
class Logger:
    def info(self, msg): print(f"INFO: {msg}")
    def warning(self, msg): print(f"WARN: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")

logger = Logger()

# Mock config
def config(key, default=''):
    return os.environ.get(key, default)

class MetaDefenderService:
    def __init__(self):
        self.api_key = config('METADEFENDER_API_KEY', default='')
        self.base_url = 'https://api.metadefender.com/v4'
        if not self.api_key:
            print("WARNING: METADEFENDER_API_KEY not found in env")
    
    def check_apikey(self):
        url = f"{self.base_url}/apikey"
        headers = {'apikey': self.api_key}
        print(f"Checking API Key at {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"API Key Check: {resp.status_code}")
            if resp.status_code != 200:
                print(f"API Key Error: {resp.text}")
            else:
                print("API Key OK")
                print(resp.json())
        except Exception as e:
            print(f"API Key Check Exception: {e}")

    def analyze_url(self, url):
        import urllib.parse
        # Analiza una URL
        if not self.api_key:
             return {'error': 'Falta la clave de API'}

        try:
            logger.info(f"[MD] Analizando URL: {url}")
            
            # TRY LOOKUP FIRST
            encoded_url = urllib.parse.quote(url, safe='')
            lookup_url = f"{self.base_url}/url/{encoded_url}"
            headers = {'apikey': self.api_key}
            
            print(f"Lookup URL: {lookup_url}")
            resp_lookup = requests.get(lookup_url, headers=headers, timeout=10)
            print(f"Lookup Res: {resp_lookup.status_code}")
            
            if resp_lookup.status_code == 200:
                print("Lookup SUCCESS")
                return resp_lookup.json()
            
            # If not found, submit
            submit_url = f"{self.base_url}/url"
            # ... (rest of code)
            headers = {
                'apikey': self.api_key,
                'User-Agent': 'Python-Client/1.0',
                'Content-Type': 'application/json'
            }
            print(f"Using Key: {self.api_key[:5]}...")
            payload = {'url': url}
            
            logger.info(f"Submitting to {submit_url}")
            # response = requests.post(submit_url, json=payload, headers=headers, timeout=30)
            # Use explicit data and headers
            import json
            headers['Content-Type'] = 'application/json'
            response = requests.post(submit_url, data=json.dumps(payload), headers=headers, timeout=30)
            
            print(f"DEBUG REQ HEADERS: {response.request.headers}")
            print(f"DEBUG REQ BODY: {response.request.body}")

            logger.info(f"Submit response: {response.status_code}")
            
            if response.status_code != 200:
                print(f"!!! MD ERROR STATUS: {response.status_code} !!!")
                print(f"!!! MD ERROR TEXT: {response.text} !!!")
            
            if response.status_code == 200:
                data = response.json()
                data_id = data.get('data_id')
                logger.info(f"Data ID: {data_id}")
                
                # 2. Esperar resultados (Aumentamos a 20 intentos x 3s = 60s)
                for attempt in range(20):
                    time.sleep(3)
                    result_url = f"{self.base_url}/url/{data_id}"
                    result_response = requests.get(result_url, headers=headers)
                    
                    if result_response.status_code == 200:
                        res_data = result_response.json()
                        scan_results = res_data.get('scan_results', {})
                        progress = scan_results.get('progress_percentage', 0)
                        logger.info(f"Attempt {attempt+1}: Progress {progress}%")
                        
                        # Si ya tiene resultados (aunque sea parcial) o progreso 100
                        if progress == 100 or 'total_detected_avs' in scan_results:
                            total_detected = scan_results.get('total_detected_avs', 0)
                            total_avs = scan_results.get('total_avs', 0)
                            
                            # Si total_avs es 0, es que aun esta encolado posiblemente, seguimos esperando un poco mas
                            if total_avs == 0 and attempt < 15:
                                logger.info("Total AVs is 0, waiting...")
                                continue

                            return {
                                'positives': total_detected,
                                'total': total_avs,
                                'source': 'MetaDefender',
                                'link': f"https://metadefender.opswat.com/results/url/{data_id}/overview"
                            }
            
            logger.warning(f"[MD] Timeout o error en analisis URL. Status: {response.status_code}")
            return {'error': 'Timeout o error'}

        except Exception as e:
             logger.error(f"[MD] Error URL: {e}")
             return {'error': str(e)}

if __name__ == "__main__":
    # Load env vars from .env manually since we don't have decouple handy or just read the file
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    except Exception as e:
        print(f"Error loading .env: {e}")

    md = MetaDefenderService()
    md.check_apikey()
    url = "https://google.com"
    print(f"Testing URL: {url}")
    res = md.analyze_url(url)
    print("Result:", res)
