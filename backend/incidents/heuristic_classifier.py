import logging
import re

logger = logging.getLogger(__name__)

class HeuristicClassifier:
    """
    Clasificador heurístico que analiza características del archivo/URL
    más allá de los resultados de antivirus.
    """
    
    # Extensiones de alto riesgo
    DANGEROUS_EXTENSIONS = [
        'exe', 'bat', 'cmd', 'com', 'scr', 'vbs', 'js', 'jar',
        'msi', 'dll', 'sys', 'reg', 'ps1', 'psm1', 'hta'
    ]
    
    # Extensiones de documentos con macros (riesgo medio)
    MACRO_EXTENSIONS = [
        'doc', 'docm', 'xls', 'xlsm', 'ppt', 'pptm', 'xlam'
    ]
    
    # Palabras sospechosas en nombres de archivo
    SUSPICIOUS_KEYWORDS = [
        'crack', 'keygen', 'patch', 'activator', 'loader',
        'invoice', 'factura', 'payment', 'urgent', 'urgente',
        'password', 'contraseña', 'confidential', 'admin',
        'bitcoin', 'wallet', 'recovery'
    ]
    
    # Dominios sospechosos en URLs
    SUSPICIOUS_DOMAINS = [
        '.tk', '.ml', '.ga', '.cf', '.gq',  # TLDs gratuitos
        'bit.ly', 'tinyurl', 'goo.gl',  # Acortadores
        'drive.google', 'dropbox', 'mediafire'  # Compartidos
    ]
    
    @staticmethod
    def analyze_file(filename, file_size, vt_positives, vt_total):
        """
        Analiza características heurísticas de un archivo.
        
        Returns:
            dict con risk_score (0-100) y reasons (lista de razones)
        """
        risk_score = 0
        reasons = []
        
        filename_lower = filename.lower()
        
        # 1. Análisis de extensión
        extension = filename_lower.split('.')[-1] if '.' in filename_lower else ''
        
        if extension in HeuristicClassifier.DANGEROUS_EXTENSIONS:
            risk_score += 30
            reasons.append(f"Extensión ejecutable de alto riesgo (.{extension})")
        elif extension in HeuristicClassifier.MACRO_EXTENSIONS:
            risk_score += 15
            reasons.append(f"Documento con posibles macros (.{extension})")
        
        # 2. Análisis del nombre del archivo
        for keyword in HeuristicClassifier.SUSPICIOUS_KEYWORDS:
            if keyword in filename_lower:
                risk_score += 10
                reasons.append(f"Nombre sospechoso contiene '{keyword}'")
        
        # 3. Múltiples extensiones (técnica de ofuscación)
        if filename.count('.') > 1:
            # Ejemplo: factura.pdf.exe
            risk_score += 20
            reasons.append("Múltiples extensiones (posible ofuscación)")
        
        # 4. Tamaño sospechoso
        if file_size < 10000:  # Menos de 10KB
            risk_score += 5
            reasons.append("Tamaño inusualmente pequeño")
        elif file_size > 50000000:  # Más de 50MB
            risk_score += 5
            reasons.append("Tamaño inusualmente grande")
        
        # 5. Resultados de VirusTotal
        detection_rate = (vt_positives / vt_total * 100) if vt_total > 0 else 0
        
        if detection_rate > 70:
            risk_score += 40
            reasons.append(f"Alta tasa de detección ({detection_rate:.1f}%)")
        elif detection_rate > 30:
            risk_score += 25
            reasons.append(f"Tasa moderada de detección ({detection_rate:.1f}%)")
        elif detection_rate > 5:
            risk_score += 10
            reasons.append(f"Algunos motores alertan ({detection_rate:.1f}%)")
        
        # 6. Nombre genérico/común usado en phishing
        generic_names = ['invoice', 'factura', 'payment', 'documento', 'archivo']
        if any(name in filename_lower for name in generic_names):
            risk_score += 5
            reasons.append("Nombre genérico común en phishing")
        
        # Limitar score a 100
        risk_score = min(risk_score, 100)
        
        logger.info(f"[HEURISTIC] Score: {risk_score}/100 - {len(reasons)} indicadores")
        
        return {
            'score': risk_score,
            'reasons': reasons,
            'classification': HeuristicClassifier._get_classification(risk_score)
        }
    
    @staticmethod
    def analyze_url(url, vt_positives, vt_total, is_phishing):
        """
        Analiza características heurísticas de una URL.
        """
        risk_score = 0
        reasons = []
        
        url_lower = url.lower()
        
        # 1. Dominio sospechoso
        for suspicious_domain in HeuristicClassifier.SUSPICIOUS_DOMAINS:
            if suspicious_domain in url_lower:
                risk_score += 20
                reasons.append(f"Dominio sospechoso ({suspicious_domain})")
        
        # 2. IP en lugar de dominio
        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url):
            risk_score += 25
            reasons.append("Usa dirección IP en lugar de nombre de dominio")
        
        # 3. URL excesivamente larga (>100 caracteres)
        if len(url) > 100:
            risk_score += 10
            reasons.append("URL inusualmente larga")
        
        # 4. Muchos subdominios (más de 3)
        subdomain_count = url.split('//')[1].split('/')[0].count('.') if '//' in url else 0
        if subdomain_count > 3:
            risk_score += 15
            reasons.append("Múltiples subdominios (posible ofuscación)")
        
        # 5. Caracteres especiales sospechosos
        if '@' in url or '%' in url:
            risk_score += 15
            reasons.append("Caracteres de ofuscación en URL")
        
        # 6. HTTP en lugar de HTTPS
        if url.startswith('http://'):
            risk_score += 10
            reasons.append("Conexión no cifrada (HTTP)")
        
        # 7. Resultados de detección
        if is_phishing:
            risk_score += 50
            reasons.append("Confirmado como sitio de phishing")
        
        detection_rate = (vt_positives / vt_total * 100) if vt_total > 0 else 0
        if detection_rate > 30:
            risk_score += 30
            reasons.append(f"Múltiples motores alertan ({detection_rate:.1f}%)")
        elif detection_rate > 0:
            risk_score += 15
            reasons.append(f"Algunos motores alertan ({detection_rate:.1f}%)")
        
        risk_score = min(risk_score, 100)
        
        logger.info(f"[HEURISTIC] URL Score: {risk_score}/100")
        
        return {
            'score': risk_score,
            'reasons': reasons,
            'classification': HeuristicClassifier._get_classification(risk_score)
        }
    
    @staticmethod
    def _get_classification(score):
        """
        Convierte score numérico a clasificación.
        """
        if score >= 70:
            return 'CRITICAL'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'
