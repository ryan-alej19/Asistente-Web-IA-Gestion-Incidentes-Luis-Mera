"""
🤖 SERVICIO DE GEMINI - ANÁLISIS CONTEXTUAL
Ryan Gallegos Mera - PUCESI
Última actualización: 03 de Enero, 2026
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiService:
    """
    🤖 Servicio para análisis contextual de incidentes usando Gemini 1.5 Flash
    """
    
    def __init__(self):
        """
        Inicializa el servicio de Gemini
        """
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY no está configurada en .env")
        
        genai.configure(api_key=api_key)
        
        # 🔥 CAMBIADO A GEMINI 1.5 FLASH (MÁS ESTABLE Y MAYOR CUOTA)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ GeminiService inicializado correctamente con Gemini 1.5 Flash")


    def analyze_incident(self, url, description, threat_type, severity):
        """
        🔍 Analiza un incidente de ciberseguridad usando Gemini
        
        Args:
            url (str): URL reportada (puede ser vacía)
            description (str): Descripción del incidente
            threat_type (str): Tipo de amenaza (phishing, malware, etc.)
            severity (str): Nivel de severidad detectado por IA local
        
        Returns:
            dict: Análisis contextual del incidente
        """
        try:
            print(f"\n🤖 GEMINI: Iniciando análisis...")
            print(f"   - URL: {url or 'No especificada'}")
            print(f"   - Tipo: {threat_type}")
            print(f"   - Severidad: {severity}")
            
            # 🎯 PROMPT OPTIMIZADO PARA TESIS
            prompt = f"""
Eres un asistente de ciberseguridad para pequeñas empresas.

**CONTEXTO DEL INCIDENTE:**
- Tipo de amenaza: {threat_type}
- Severidad detectada: {severity}
- URL reportada: {url or "No proporcionada"}
- Descripción: {description or "Sin descripción"}

**TU TAREA:**
Proporciona un análisis breve (máximo 200 palabras) que incluya:

1. **Explicación simple** de por qué es {severity} (en español sencillo)
2. **Patrones detectados** (máximo 3 puntos clave)
3. **Recomendación práctica** inmediata para el usuario

**IMPORTANTE:**
- Usa lenguaje NO técnico (para pequeñas empresas)
- Sé directo y práctico
- NO inventes datos técnicos
- Si no estás seguro, di "requiere revisión manual"

**FORMATO DE RESPUESTA:**
Explicación: [tu explicación]
Patrones: [lista de 2-3 patrones]
Recomendación: [acción concreta]
"""
            
            # 🚀 GENERAR RESPUESTA
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Gemini no retornó contenido válido")
            
            analysis_text = response.text.strip()
            
            # 📝 PARSEAR RESPUESTA
            result = self._parse_gemini_response(analysis_text)
            
            print(f"✅ GEMINI: Análisis completado exitosamente")
            
            return {
                'success': True,
                'explanation': result.get('explanation', analysis_text),
                'patterns_detected': result.get('patterns', []),
                'recommendation': result.get('recommendation', 'Solicitar revisión del equipo de seguridad'),
                'raw_analysis': analysis_text
            }
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ ERROR en GeminiService.analyze_incident: {error_msg}")
            
            return {
                'success': False,
                'explanation': 'Análisis contextual no disponible temporalmente',
                'patterns_detected': [],
                'recommendation': 'El incidente ha sido registrado y será revisado por el equipo de seguridad',
                'error': error_msg
            }


    def _parse_gemini_response(self, text):
        """
        📝 Parsea la respuesta de Gemini en formato estructurado
        
        Args:
            text (str): Texto de respuesta de Gemini
        
        Returns:
            dict: Datos estructurados
        """
        try:
            lines = text.split('\n')
            result = {
                'explanation': '',
                'patterns': [],
                'recommendation': ''
            }
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                
                # Detectar secciones
                if 'Explicación:' in line or 'Explicacion:' in line:
                    current_section = 'explanation'
                    result['explanation'] = line.split(':', 1)[1].strip()
                
                elif 'Patrones:' in line:
                    current_section = 'patterns'
                    pattern_text = line.split(':', 1)[1].strip()
                    if pattern_text:
                        result['patterns'].append(pattern_text)
                
                elif 'Recomendación:' in line or 'Recomendacion:' in line:
                    current_section = 'recommendation'
                    result['recommendation'] = line.split(':', 1)[1].strip()
                
                # Agregar contenido a la sección actual
                elif current_section:
                    if current_section == 'explanation' and not result['explanation']:
                        result['explanation'] += line
                    elif current_section == 'patterns' and (line.startswith('-') or line.startswith('•')):
                        result['patterns'].append(line.lstrip('-•').strip())
                    elif current_section == 'recommendation' and not result['recommendation']:
                        result['recommendation'] += line
            
            # Validar que al menos tengamos explicación
            if not result['explanation']:
                result['explanation'] = text[:300]  # Primeros 300 caracteres
            
            return result
        
        except Exception as e:
            print(f"⚠️ Error parseando respuesta de Gemini: {e}")
            return {
                'explanation': text[:300] if text else "Análisis no disponible",
                'patterns': [],
                'recommendation': 'Revisión manual recomendada'
            }
