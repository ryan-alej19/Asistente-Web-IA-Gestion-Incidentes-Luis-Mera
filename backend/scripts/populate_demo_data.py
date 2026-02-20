
import os
import django
import sys
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident
from django.contrib.auth.models import User
from users.models import UserProfile

def populate():
    print("--- PREPARANDO SISTEMA PARA DEMO TESIS ---")

    # 2. Usuarios (siempre crear/actualizar)
    users_data = [
        {'username': 'empleado', 'email': 'empleado@tecnicontrol.com', 'role': 'employee', 'password': 'empleado123'},
        {'username': 'analista', 'email': 'analista@tecnicontrol.com', 'role': 'analyst', 'password': 'analista123'},
        {'username': 'admin', 'email': 'admin@tecnicontrol.com', 'role': 'admin', 'password': 'admin123'}
    ]

    users_objs = {}
    for u_data in users_data:
        user, created = User.objects.get_or_create(username=u_data['username'], defaults={'email': u_data['email']})
        if created:
            user.set_password(u_data['password'])
            user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = u_data['role']
        profile.save()
        users_objs[u_data['username']] = user

    print(f"  Usuarios listos: {list(users_objs.keys())}")

    # GUARDIA: Solo poblar si la BD esta completamente vacia
    existing = Incident.objects.count()
    if existing > 0:
        print(f"  Ya existen {existing} incidentes. Saltando seed inicial.")
        print("--- SISTEMA LISTO ---")
        return

    print("  BD vacia - creando 24 incidentes iniciales...")

    # helper for gemini text
    def get_gemini_text(risk, type_):
        if risk == 'CRITICAL': return "ALERTA CRÍTICA: Amenaza confirmada con alta confianza. Se detectan patrones maliciosos conocidos."
        if risk == 'HIGH': return "ALERTA: Alta probabilidad de amenaza. Múltiples motores detectan actividad sospechosa."
        if risk == 'MEDIUM': return "PRECAUCIÓN: Elementos sospechosos detectados. Se recomienda revisión manual."
        if risk == 'LOW': return "BAJO RIESGO: Pocos indicadores de compromiso, probablemente falso positivo o adware."
        return "SEGURO: No se encontraron amenazas en el análisis."

    incidents_list = [
        # --- A. URLs PELIGROSAS (10) ---
        { 'title': 'URL Malware Google Test', 'desc': 'URL sospechosa recibida por correo (Malware)', 'target': 'http://malware.testing.google.test/testing/malware/', 'type': 'url', 'risk': 'CRITICAL', 'status': 'resolved', 'vt': {'positives': 15, 'total': 90} },
        { 'title': 'Phishing Test Page', 'desc': 'Enlace de correo bancario sospechoso (Phishing)', 'target': 'http://testsafebrowsing.appspot.com/s/phishing.html', 'type': 'url', 'risk': 'CRITICAL', 'status': 'investigating', 'vt': {'positives': 12, 'total': 90} },
        { 'title': 'Malware Download Test', 'desc': 'Descarga automática desde enlace desconocido', 'target': 'http://testsafebrowsing.appspot.com/s/malware.html', 'type': 'url', 'risk': 'CRITICAL', 'status': 'resolved', 'vt': {'positives': 20, 'total': 90} },
        { 'title': 'EICAR Web Download', 'desc': 'Archivo de prueba EICAR desde sitio web', 'target': 'http://eicar.org/download/eicar.com', 'type': 'url', 'risk': 'HIGH', 'status': 'investigating', 'vt': {'positives': 60, 'total': 90} },
        { 'title': 'SRI Datos Falsos', 'desc': 'Supuesto portal del SRI solicitando datos (Phishing)', 'target': 'http://sri-actualizacion-datos.info/login', 'type': 'url', 'risk': 'MEDIUM', 'status': 'pending', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'BCE Verificación', 'desc': 'Correo del supuesto Banco Central (Phishing)', 'target': 'http://bce-verificacion-cuenta.com/acceso', 'type': 'url', 'risk': 'HIGH', 'status': 'pending', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'IESS Falso', 'desc': 'Portal falso del IESS (Phishing)', 'target': 'http://iess-consulta-beneficios.net/validar', 'type': 'url', 'risk': 'MEDIUM', 'status': 'investigating', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'Pichincha Phishing', 'desc': 'Correo de Banco Pichincha sospechoso', 'target': 'http://pichincha-seguridad-online.xyz/confirmar', 'type': 'url', 'risk': 'HIGH', 'status': 'pending', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'WhatsApp Fake', 'desc': 'Enlace de WhatsApp malicioso', 'target': 'http://actualizacion-whatsapp-gratis.site/download', 'type': 'url', 'risk': 'MEDIUM', 'status': 'pending', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'Amazon Scam', 'desc': 'Correo de supuesto premio de Amazon', 'target': 'http://premio-amazon-ecuador.click/reclamar', 'type': 'url', 'risk': 'MEDIUM', 'status': 'pending', 'vt': {'positives': 0, 'total': 90} },
        # --- B. URLs SEGURAS (4) ---
        { 'title': 'Google', 'desc': 'Validación de sitio legítimo', 'target': 'https://www.google.com', 'type': 'url', 'risk': 'LOW', 'status': 'resolved', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'PUCESI', 'desc': 'Portal oficial de la universidad', 'target': 'https://www.pucesi.edu.ec', 'type': 'url', 'risk': 'LOW', 'status': 'resolved', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'YouTube Video', 'desc': 'Video compartido por cliente', 'target': 'https://www.youtube.com', 'type': 'url', 'risk': 'LOW', 'status': 'investigating', 'vt': {'positives': 0, 'total': 90} },
        { 'title': 'Wikipedia', 'desc': 'Enlace de referencia', 'target': 'https://www.wikipedia.org', 'type': 'url', 'risk': 'LOW', 'status': 'resolved', 'vt': {'positives': 0, 'total': 90} },
        # --- C. ARCHIVOS MALICIOSOS (4) ---
        { 'title': 'Factura SRI.exe', 'desc': 'Factura adjunta en correo del SRI (Malware)', 'target': 'factura_sri_2025.pdf.exe', 'type': 'file', 'risk': 'CRITICAL', 'status': 'investigating', 'vt': {'positives': 72, 'total': 90} },
        { 'title': 'Pago BCE.exe', 'desc': 'Comprobante del Banco Central Malicioso', 'target': 'comprobante_pago_bce.exe', 'type': 'file', 'risk': 'CRITICAL', 'status': 'resolved', 'vt': {'positives': 68, 'total': 90} },
        { 'title': 'Update IESS.exe', 'desc': 'Actualización del sistema IESS Fake', 'target': 'actualizacion_iess.exe', 'type': 'file', 'risk': 'CRITICAL', 'status': 'pending', 'vt': {'positives': 75, 'total': 90} },
        { 'title': 'Catalogo.xlsx.exe', 'desc': 'Catálogo enviado por proveedor (Ransomware)', 'target': 'catalogo_repuestos.xlsx.exe', 'type': 'file', 'risk': 'CRITICAL', 'status': 'investigating', 'vt': {'positives': 70, 'total': 90} },
        # --- D. SOLO DESCRIPCIÓN (6) ---
        { 'title': 'Word con Macros', 'desc': 'Documento Word recibido de cliente nuevo con macros habilitadas', 'target': '', 'type': 'file', 'risk': 'HIGH', 'status': 'investigating', 'vt': {'positives': 0, 'total': 0} },
        { 'title': 'PDF Link Phishing', 'desc': 'PDF con enlace sospechoso enviado por proveedor desconocido', 'target': '', 'type': 'file', 'risk': 'MEDIUM', 'status': 'pending', 'vt': {'positives': 0, 'total': 0} },
        { 'title': 'ZIP con Pass', 'desc': 'Archivo ZIP protegido con contraseña de remitente extraño', 'target': '', 'type': 'file', 'risk': 'MEDIUM', 'status': 'pending', 'vt': {'positives': 0, 'total': 0} },
        { 'title': 'JPG Grande', 'desc': 'Imagen JPG de factura con tamaño inusualmente grande', 'target': '', 'type': 'file', 'risk': 'LOW', 'status': 'resolved', 'vt': {'positives': 0, 'total': 0} },
        { 'title': 'Installer Unknown', 'desc': 'Instalador de software de origen no verificado', 'target': '', 'type': 'file', 'risk': 'MEDIUM', 'status': 'investigating', 'vt': {'positives': 0, 'total': 0} },
        { 'title': 'Backup Externo', 'desc': 'Backup del sistema solicitado por técnico externo', 'target': '', 'type': 'file', 'risk': 'LOW', 'status': 'resolved', 'vt': {'positives': 0, 'total': 0} }
    ]

    count = 0
    # Start from Dec 1, 2025 so they appear chronologically before the inject data
    from datetime import datetime
    start_date = datetime(2025, 12, 1, 8, 0, 0, tzinfo=timezone.utc)

    for i, item in enumerate(incidents_list):
        created_at = start_date + timedelta(hours=i*8) 
        
        url_val = item['target'] if 'http' in item.get('target', '') else None
        file_val = None
        if item.get('target') and not url_val:
            file_val = f"uploads/{item['target']}"
        
        inc = Incident.objects.create(
            description=f"[{item['title']}] {item['desc']}",
            incident_type=item['type'],
            risk_level=item['risk'],
            status=item['status'],
            reported_by=users_objs['empleado'],
            url=url_val,
            attached_file=file_val,
            analysis_result={
                'engines': [{'name': 'VirusTotal', 'positives': item['vt']['positives'], 'total': item['vt']['total']}],
                'gemini_recomendacion': get_gemini_text(item['risk'], item['type']),
                'gemini_explicacion': get_gemini_text(item['risk'], item['type'])
            },
            gemini_analysis=get_gemini_text(item['risk'], item['type'])
        )
        
        # Force create date
        inc.created_at = created_at
        inc.save()
        count += 1
        print(f"[{i+1}/{len(incidents_list)}] Creado: {item['title']} ({item['type']}/{item['risk']}/{item['status']})")

    print(f"\nGenerados {count} incidentes de prueba (CORREGIDOS) exitosamente.")
    print("--- SISTEMA LISTO PARA DEMO LOCAL ---")

if __name__ == '__main__':
    populate()
