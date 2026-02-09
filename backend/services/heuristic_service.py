import re
import logging
import os

logger = logging.getLogger(__name__)

class HeuristicService:
    def __init__(self):
        # Patrones sospechosos para URLs
        self.suspicious_keywords_url = [
            'login', 'signin', 'bank', 'verify', 'update', 'account', 
            'secure', 'banking', 'confirm', 'wallet', 'crypto', 'unlock',
            'suspended', 'urgent', 'password', 'credential', 'paypal', 
            'amazon', 'microsoft', 'support', 'apple', 'icloud'
        ]
        
        # Dominios conocidos de phishing o typosquatting (ejemplos)
        self.suspicious_domains = [
            'g00gle', 'faceb00k', 'paypa1', 'micros0ft', 'appe', 'nelfix',
            '0ffice', 'hotmai1', 'gmai1'
        ]
        
        # Extensiones peligrosas para archivos
        self.dangerous_extensions = [
            '.exe', '.bat', '.cmd', '.sh', '.vbs', '.js', '.scr', '.pif', 
            '.application', '.gadget', '.msi', '.msp', '.com', '.hta', 
            '.cpl', '.msc', '.jar'
        ]
        
        # Palabras clave en nombres de archivos (Ingeniería Social)
        self.suspicious_filenames = [
            'factura', 'invoice', 'receipt', 'urgente', 'urgent', 
            'pago', 'payment', 'documento', 'scan', 'img', 'foto',
            'premio', 'ganador', 'oferta', 'contrato', 'nomina'
        ]

    def analyze_url(self, url):
        """Analiza una URL buscando patrones sospechosos con lógica refinada."""
        logger.info(f"Iniciando análisis heurístico para URL: {url}")
        
        from urllib.parse import urlparse
        import re
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            if not domain and parsed.path: # Caso donde no hay esquema (ej: google.com)
                 domain = parsed.path.split('/')[0]
            
            # Limpiar posible puerto
            if ':' in domain:
                domain = domain.split(':')[0]
                
        except Exception:
            domain = url.lower() # Fallback
            
        detected_patterns = []
        risk_score = 0
        
        # Palabras clave (reducidas a las más críticas para evitar ruido)
        keywords = [
            'login', 'signin', 'bank', 'verify', 'update', 'account', 
            'secure', 'banking', 'confirm', 'wallet', 'suspended', 
            'urgent', 'password', 'unlock', 'paypal', 'amazon'
        ]
        
        # 1. Palabras clave SOLO en el dominio
        domain_keywords = [k for k in keywords if k in domain]
        
        if len(domain_keywords) >= 2:
            detected_patterns.append(f"Múltiples palabras clave en dominio: {', '.join(domain_keywords)}")
            risk_score += 3 # ALTO
        elif len(domain_keywords) == 1:
            # Una sola palabra es sospechosa pero puede ser 'login.microsoft.com' (legitimo)
            # Verificamos si es un dominio de confianza
            trusted_domains = ['google.com', 'microsoft.com', 'live.com', 'amazon.com', 'paypal.com', 'apple.com', 'facebook.com']
            is_trusted = any(domain.endswith(td) for td in trusted_domains)
            
            if not is_trusted:
                detected_patterns.append(f"Palabra clave en dominio no confiable: '{domain_keywords[0]}'")
                risk_score += 1 # MEDIO
        
        # 2. Uso de IP en lugar de dominio
        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', domain):
            detected_patterns.append("Uso de dirección IP directa")
            risk_score += 2 # ALTO
            
        # 3. Dominios falsos (Typosquatting)
        fake_keywords = ['g00gle', 'faceb00k', 'paypa1', 'micros0ft', 'appe', 'nelfix', '0ffice', 'hotmai1', 'gmai1']
        found_fakes = [fake for fake in fake_keywords if fake in domain]
        if found_fakes:
             detected_patterns.append(f"Posible suplantación de dominio: {', '.join(found_fakes)}")
             risk_score += 3 # ALTO
             
        # 4. Longitud excesiva de dominio (no URL completa)
        if len(domain) > 50:
            detected_patterns.append("Nombre de dominio inusualmente largo")
            risk_score += 1

        # Resultado
        is_suspicious = risk_score >= 1
        
        if risk_score >= 3:
            risk_factor = 'CRITICO'
        elif risk_score >= 2:
            risk_factor = 'ALTO'
        elif risk_score == 1:
            risk_factor = 'MEDIO'
        else:
            risk_factor = 'BAJO'
            
        result = {
            'heuristic_alert': is_suspicious,
            'detected_patterns': detected_patterns,
            'risk_factor': risk_factor
        }
        
        return result

    def analyze_file(self, filename, filesize=0):
        """Analiza un nombre de archivo buscando patrones sospechosos."""
        logger.info(f"Iniciando análisis heurístico para archivo: {filename}")
        detected_patterns = []
        risk_score = 0
        
        filename_lower = filename.lower()
        name, extension = os.path.splitext(filename_lower)
        
        # 1. Verificar extensión peligrosa
        if extension in self.dangerous_extensions:
            detected_patterns.append(f"Extensión ejecutable/peligrosa: '{extension}'")
            risk_score += 3 # Muy alto riesgo
            
        # 2. Doble extensión (ej: factura.pdf.exe)
        # Buscamos si hay otro punto en el nombre (ignorando el inicial si existe)
        if '.' in name:
            # Check if the part before the last dot looks like a safe extension
            parts = name.rsplit('.', 1)
            if len(parts) > 1:
                fake_ext = '.' + parts[1]
                safe_exts = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.txt']
                if fake_ext in safe_exts:
                    detected_patterns.append(f"Posible doble extensión (camuflado como {fake_ext})")
                    risk_score += 2
        
        # 3. Palabras clave de ingeniería social
        for keyword in self.suspicious_filenames:
            if keyword in filename_lower:
                detected_patterns.append(f"Nombre con posible ingeniería social: '{keyword}'")
                risk_score += 0.5

        # Resultado
        is_suspicious = risk_score >= 1
        
        result = {
            'heuristic_alert': is_suspicious,
            'detected_patterns': detected_patterns,
            'risk_factor': 'CRITICO' if risk_score >= 3 else ('ALTO' if risk_score >= 2 else ('MEDIO' if risk_score >= 1 else 'BAJO'))
        }
        
        return result
