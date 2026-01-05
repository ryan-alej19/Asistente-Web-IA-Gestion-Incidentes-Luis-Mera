"""
🛡️ SERVICIO VIRUSTOTAL + GEMINI AI - TESIS CIBERSEGURIDAD
Ryan Gallegos Mera - PUCESI
Última actualización: 03 de Enero, 2026
"""

import requests
import time
import os
import google.generativeai as genai
from django.conf import settings
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class VirusTotalService:
    """
    Servicio para integrar con la API de VirusTotal v3
    Límites cuenta gratuita: 500 requests/día, 4 requests/minuto
    """
    BASE_URL = "https://www.virustotal.com/api/v3"
    
    def __init__(self):
        self.api_key = getattr(settings, 'VIRUSTOTAL_API_KEY', None)
        self.headers = {
            "x-apikey": self.api_key,
            "Accept": "application/json"
        }
    
    def analyze_url(self, url):
        """
        Analiza una URL con VirusTotal
        
        Args:
            url (str): URL a analizar
            
        Returns:
            dict: {
                'success': bool,
                'detections': int,
                'total_engines': int,
                'malicious': int,
                'suspicious': int,
                'harmless': int,
                'undetected': int,
                'permalink': str,
                'error': str (opcional)
            }
        """
        if not self.api_key:
            return self._error_response("API Key de VirusTotal no configurada")
        
        try:
            print(f"\n{'='*60}")
            print(f"🛡️ ANALIZANDO URL CON VIRUSTOTAL: {url}")
            print(f"{'='*60}")
            
            # Paso 1: Enviar URL para análisis
            scan_url = f"{self.BASE_URL}/urls"
            payload = {"url": url}
            
            response = requests.post(
                scan_url, 
                headers=self.headers, 
                data=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"❌ Error HTTP: {response.status_code}")
                return self._error_response(f"Error HTTP {response.status_code}")
            
            analysis_id = response.json()["data"]["id"]
            print(f"✅ URL enviada - Analysis ID: {analysis_id}")
            
            # Paso 2: Esperar 3 segundos para que VirusTotal procese
            print("⏳ Esperando análisis...")
            time.sleep(3)
            
            # Paso 3: Obtener resultado del análisis
            result_url = f"{self.BASE_URL}/analyses/{analysis_id}"
            result_response = requests.get(result_url, headers=self.headers, timeout=15)
            
            if result_response.status_code != 200:
                print(f"❌ Error obteniendo resultado: {result_response.status_code}")
                return self._error_response("Error al obtener análisis")
            
            data = result_response.json()["data"]["attributes"]
            stats = data.get("stats", {})
            
            # Extraer estadísticas
            malicious = stats.get("malicious", 0)
            suspicious = stats.get("suspicious", 0)
            harmless = stats.get("harmless", 0)
            undetected = stats.get("undetected", 0)
            
            total_engines = malicious + suspicious + harmless + undetected
            detections = malicious + suspicious
            
            result = {
                "success": True,
                "detections": detections,
                "total_engines": total_engines,
                "malicious": malicious,
                "suspicious": suspicious,
                "harmless": harmless,
                "undetected": undetected,
                "permalink": f"https://www.virustotal.com/gui/url/{analysis_id}",
                "detection_rate": round((detections / total_engines * 100), 2) if total_engines > 0 else 0
            }
            
            print(f"✅ ANÁLISIS COMPLETO:")
            print(f"   Detecciones: {detections}/{total_engines}")
            print(f"   Malicioso: {malicious}")
            print(f"   Sospechoso: {suspicious}")
            print(f"   Tasa detección: {result['detection_rate']}%")
            print(f"{'='*60}\n")
            
            return result
            
        except requests.exceptions.Timeout:
            print("❌ TIMEOUT - VirusTotal no respondió")
            return self._error_response("Timeout - VirusTotal no respondió a tiempo")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ ERROR DE CONEXIÓN: {str(e)}")
            return self._error_response(f"Error de conexión: {str(e)}")
        
        except KeyError as e:
            print(f"❌ ERROR EN RESPUESTA: Campo faltante {str(e)}")
            return self._error_response("Respuesta inválida de VirusTotal")
        
        except Exception as e:
            print(f"❌ ERROR INESPERADO: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._error_response(f"Error inesperado: {str(e)}")
    
    def _error_response(self, message):
        """Respuesta estándar para errores"""
        return {
            "success": False,
            "detections": 0,
            "total_engines": 0,
            "malicious": 0,
            "suspicious": 0,
            "harmless": 0,
            "undetected": 0,
            "error": message,
            "permalink": None,
            "detection_rate": 0
        }


# =========================================================
# 🤖 SERVICIO GEMINI AI
# =========================================================

def analyze_with_gemini(incident_data):
    """
    Analiza un incidente de ciberseguridad con Gemini AI
    
    Args:
        incident_data (dict): {
            'incident_type': str,
            'description': str,
            'url': str (opcional),
            'virustotal_result': dict (opcional)
        }
        
    Returns:
        dict: {
            'success': bool,
            'risk_level': str,
            'analysis': str,
            'recommendations': str,
            'confidence': float,
            'error': str (opcional)
        }
    """
    try:
        print(f"\n{'='*60}")
        print(f"🤖 ANALIZANDO CON GEMINI AI")
        print(f"{'='*60}")
        
        if not GEMINI_API_KEY:
            print("❌ GEMINI API KEY NO CONFIGURADA")
            return {
                "success": False,
                "error": "Gemini API key no configurada",
                "risk_level": "DESCONOCIDO",
                "analysis": "No se pudo realizar análisis con IA",
                "recommendations": "Configure la API key de Gemini",
                "confidence": 0.0
            }
        
        # Crear el modelo
        model = genai.GenerativeModel('gemini-pro')
        
        # Construir el prompt
        vt_info = ""
        if 'virustotal_result' in incident_data and incident_data['virustotal_result'].get('success'):
            vt = incident_data['virustotal_result']
            vt_info = f"""
            
**Análisis VirusTotal:**
- Detecciones: {vt.get('detections', 0)}/{vt.get('total_engines', 0)}
- Maliciosos: {vt.get('malicious', 0)}
- Sospechosos: {vt.get('suspicious', 0)}
- Tasa de detección: {vt.get('detection_rate', 0)}%
            """
        
        prompt = f"""
Eres un analista de ciberseguridad experto. Analiza el siguiente incidente de seguridad:

**Tipo de Incidente:** {incident_data.get('incident_type', 'No especificado')}
**Descripción:** {incident_data.get('description', 'Sin descripción')}
**URL reportada:** {incident_data.get('url', 'No proporcionada')}
{vt_info}

Por favor, proporciona:

1. **NIVEL DE RIESGO** (responde SOLO: ALTO, MEDIO o BAJO)
2. **ANÁLISIS TÉCNICO** (máximo 3 oraciones explicando el riesgo)
3. **RECOMENDACIONES** (3 acciones concretas que el empleado debe tomar)
4. **CONFIANZA** (porcentaje de certeza de tu análisis, ejemplo: 85)

Formato de respuesta:
NIVEL_RIESGO: [ALTO/MEDIO/BAJO]
ANÁLISIS: [tu análisis]
RECOMENDACIONES: [tus recomendaciones]
CONFIANZA: [número entre 0-100]
"""
        
        print("📤 Enviando prompt a Gemini...")
        response = model.generate_content(prompt)
        response_text = response.text
        
        print(f"✅ Respuesta recibida:\n{response_text[:200]}...")
        
        # Extraer información de la respuesta
        risk_level = "MEDIO"  # Por defecto
        analysis = ""
        recommendations = ""
        confidence = 75.0
        
        lines = response_text.split('\n')
        for line in lines:
            if 'NIVEL_RIESGO:' in line:
                risk_level = line.split(':')[1].strip()
            elif 'ANÁLISIS:' in line:
                analysis = line.split(':', 1)[1].strip()
            elif 'RECOMENDACIONES:' in line:
                recommendations = line.split(':', 1)[1].strip()
            elif 'CONFIANZA:' in line:
                try:
                    confidence = float(line.split(':')[1].strip().replace('%', ''))
                except:
                    confidence = 75.0
        
        # Si no se pudo extraer, usar todo el texto
        if not analysis:
            analysis = response_text
        
        result = {
            "success": True,
            "risk_level": risk_level,
            "analysis": analysis,
            "recommendations": recommendations,
            "confidence": confidence,
            "full_response": response_text
        }
        
        print(f"✅ ANÁLISIS GEMINI COMPLETO:")
        print(f"   Riesgo: {risk_level}")
        print(f"   Confianza: {confidence}%")
        print(f"{'='*60}\n")
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR EN GEMINI AI: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e),
            "risk_level": "DESCONOCIDO",
            "analysis": "Error al procesar con Gemini AI",
            "recommendations": "Contacte al equipo de seguridad",
            "confidence": 0.0
        }
