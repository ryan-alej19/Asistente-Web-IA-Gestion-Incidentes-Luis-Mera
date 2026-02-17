
import os
import django
import sys
import random
import json
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident, IncidentNote
from django.contrib.auth.models import User

def populate():
    print("--- INICIANDO SISTEMA CON DATOS DE DEMOSTRACIÓN ---")
    
    # 1. Limpiar base de datos
    print("Preparando entorno limpio...")
    Incident.objects.all().delete()
    
    # 2. Obtener usuarios clave
    try:
        empleado = User.objects.get(username='empleado')
        analista = User.objects.get(username='analista') # Opcional
    except User.DoesNotExist:
        # En producción/render, create_users.py ya debería haber corrido antes o necesitamos crearlos aquí si no existen
        # Para seguridad, intentamos crearlos o fallamos silenciosamente
        print("Usuarios no encontrados, intentando provisión básica...")
        try:
             # Basic fallback
             if not User.objects.filter(username='empleado').exists():
                 User.objects.create_user('empleado', 'empleado@tecnicontrol.com', 'empleado123')
             empleado = User.objects.get(username='empleado')
        except:
            print("Error crítico: No se pudo obtener usuario 'empleado'.")
            return

    # 3. Definir datos falsos realistas (Los mismos 24 casos de la tesis)
    
    # 14 URLs (Mix de Phishing, Malware, Safe)
    urls_data = [
        ("http://login-verify-account-update.com", "CRITICAL", "Phishing Bancario", "pending"),
        ("http://free-minecraft-skins.xyz/dl.exe", "HIGH", "Malware Descarga", "investigating"),
        ("https://google.com/search?q=test", "LOW", "Sitio Legítimo", "resolved"),
        ("http://192.168.1.50/admin", "MEDIUM", "Panel Interno Expuesto", "investigating"),
        ("https://secure-paypal-check.net", "CRITICAL", "Robo de Credenciales", "resolved"),
        ("http://win-update-critical.info", "HIGH", "Falso Update Windows", "pending"),
        ("https://facebook.com", "LOW", "Red Social Segura", "resolved"),
        ("http://crypto-giant-investment.biz", "HIGH", "Estafa Cripto", "investigating"),
        ("https://talleresluismera.com", "LOW", "Sitio Corporativo", "resolved"),
        ("http://urgent-delivery-dhl-truck.com", "MEDIUM", "Phishing Logística", "pending"),
        ("https://github.com/torvalds/linux", "LOW", "Repositorio Código", "resolved"),
        ("http://adult-content-free-Video.ru", "CRITICAL", "Sitio Malicioso Adulto", "investigating"),
        ("https://microsoft.com", "LOW", "Sitio Oficial", "resolved"),
        ("http://verify-bank-security-alert.net", "CRITICAL", "Phishing Genérico", "pending"),
    ]

    # 10 Archivos (Ransomware, Spyware, Clean)
    files_data = [
        ("factura_pendiente_pago.pdf.exe", "CRITICAL", "Ransomware Ryuk", "investigating"),
        ("presupuesto_taller_2024.xlsx", "LOW", "Documento Limpio", "resolved"),
        ("foto_reparacion_motor.jpg", "LOW", "Imagen Segura", "resolved"),
        ("crack_adobe_photoshop.zip", "HIGH", "Trojan Downloader", "pending"),
        ("nominas_empleados.docx", "LOW", "Documento RRHH", "resolved"),
        ("update_driver_nvidia.msi", "MEDIUM", "Adware Potencial", "investigating"),
        ("carta_recomendacion.pdf", "LOW", "PDF Legítimo", "resolved"),
        ("keygen_office_2021.exe", "CRITICAL", "Keylogger Spyware", "pending"),
        ("manual_procedimientos.pdf", "LOW", "Manual Interno", "resolved"),
        ("urgente_leer.vbs", "HIGH", "Script Malicioso", "pending"),
    ]

    all_cases = []
    
    # Mezclar y asignar fechas (8 semanas)
    base_time = timezone.now()
    
    # Generar casos URL
    for url, risk, desc, status in urls_data:
        days_ago = random.randint(1, 56)
        created_at = base_time - timedelta(days=days_ago, hours=random.randint(0, 12), minutes=random.randint(0, 59))
        all_cases.append({
            'type': 'url',
            'target': url,
            'risk': risk,
            'desc': desc,
            'status': status,
            'date': created_at
        })

    # Generar casos Archivo
    for fname, risk, desc, status in files_data:
        days_ago = random.randint(1, 56)
        created_at = base_time - timedelta(days=days_ago, hours=random.randint(0, 12), minutes=random.randint(0, 59))
        all_cases.append({
            'type': 'file',
            'target': fname,
            'risk': risk,
            'desc': desc,
            'status': status,
            'date': created_at
        })

    all_cases.sort(key=lambda x: x['date'])

    print(f"Total registros a procesar: {len(all_cases)}")

    # Inserción
    for case in all_cases:
        # Simular respuestas JSON de APIs
        vt_dummy = {'positives': 0, 'total': 90}
        if case['risk'] in ['CRITICAL', 'HIGH']:
            vt_dummy['positives'] = random.randint(15, 60)
        elif case['risk'] == 'MEDIUM':
            vt_dummy['positives'] = random.randint(3, 10)
        
        gemini_dummy = {
            "explicacion": f"Análisis simulado por IA: El recurso '{case['target']}' presenta indicadores de {case['risk']}. {case['desc']}.",
            "recomendacion": "Bloquear acceso y reportar inmediatamente." if case['risk'] in ['CRITICAL', 'HIGH'] else "Proceder con precaución."
        }
        
        full_analysis = {
            "risk_level": case['risk'],
            "details": f"Detección manual simulada para {case['desc']}",
            "providers": ["VirusTotal", "MetaDefender", "Gemini AI"]
        }

        inc = Incident(
            incident_type=case['type'],
            url=case['target'] if case['type'] == 'url' else None,
            attached_file=case['target'] if case['type'] == 'file' else None, 
            description=f"Reporte automático de {case['desc']}",
            risk_level=case['risk'],
            status=case['status'],
            reported_by=empleado,
            virustotal_result=vt_dummy,
            gemini_analysis=json.dumps(gemini_dummy),
            analysis_result=full_analysis,
            created_at=case['date'],
            updated_at=case['date']
        )
        
        if case['type'] == 'file':
             inc.attached_file.name = f'incidents/{case["target"]}'

        inc.save()
        Incident.objects.filter(id=inc.id).update(created_at=case['date'], updated_at=case['date'])
        
        print(f"Registro ID {inc.id}: {case['target']}")

    print("\n--- SISTEMA INICIALIZADO CORRECTAMENTE ---")

if __name__ == '__main__':
    populate()
