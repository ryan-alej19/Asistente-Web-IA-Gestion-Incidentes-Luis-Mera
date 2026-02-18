
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
    print("--- PREPARANDO SISTEMA PARA DEMO (DATOS REALISTAS) ---")
    
    # 1. Limpiar (Opcional, para demo siempre limpio es mejor)
    print("Limpiando base de datos...")
    Incident.objects.all().delete()
    
    # 2. Usuarios
    print("Verificando usuarios...")
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
            print(f"Usuario creado: {u_data['username']}")
        
        # Profile
        UserProfile.objects.get_or_create(user=user, defaults={'role': u_data['role']})
        users_objs[u_data['username']] = user

    # 3. Incidentes (15-20)
    print("Generando incidentes de prueba...")
    
    incident_templates = [
        {
            'title': 'Correo Sospechoso de Banco',
            'desc': 'Recibí un correo pidiendo actualizar mis datos bancarios. El link es extraño.',
            'type': 'phishing',
            'risk': 'high',
            'status': 'investigating',
            'target': 'http://bancopichincha-seguro-login.xyz',
            'vt_score': {'positives': 15, 'total': 90},
            'gemini': 'Alta probabilidad de Phishing. El dominio .xyz es común en estafas.'
        },
        {
            'title': 'Factura.pdf.exe',
            'desc': 'Un archivo adjunto que parece una factura pero tiene doble extensión.',
            'type': 'malware',
            'risk': 'critical',
            'status': 'closed',
            'target': 'Factura_Pendiente_2024.pdf.exe',
            'vt_score': {'positives': 45, 'total': 90},
            'gemini': 'Malware confirmado. Archivo ejecutable camuflado como PDF (Double Extension).'
        },
        {
            'title': 'Página de Login Corporativo',
            'desc': 'La página interna de RRHH carga lento y pide login de nuevo.',
            'type': 'url',
            'risk': 'safe',
            'status': 'analyzed',
            'target': 'https://rrhh.tecnicontrol.com/login',
            'vt_score': {'positives': 0, 'total': 90},
            'gemini': 'Sitio legítimo. La lentitud puede deberse a problemas de red interna.'
        },
        {
            'title': 'Alerta de Antivirus en PC Ventas',
            'desc': 'El antivirus saltó al conectar un USB de un cliente.',
            'type': 'ransomware',
            'risk': 'high',
            'status': 'investigating',
            'target': 'USB_Drive_G:/Autorun.inf',
            'vt_score': {'positives': 22, 'total': 90},
            'gemini': 'Posible vector de infección por USB (Worm/Ransomware).'
        },
        {
            'title': 'Enlace de Zoom desconocido',
            'desc': 'Invitación a reunión de Zoom de un remitente externo.',
            'type': 'phishing',
            'risk': 'medium',
            'status': 'analyzed',
            'target': 'https://zoom-meetings-secure.net/join',
            'vt_score': {'positives': 4, 'total': 90},
            'gemini': 'Dominio sospechoso (Cybersquatting). No es el dominio oficial de Zoom.'
        },
         {
            'title': 'Archivo Excel con Macros',
            'desc': 'Contabilidad reporta un Excel que pide habilitar macros para ver el contenido.',
            'type': 'malware',
            'risk': 'critical',
            'status': 'pending',
            'target': 'Balance_General_2025.xlsm',
            'vt_score': {'positives': 35, 'total': 88},
            'gemini': 'Documento malicioso. Contiene macros VBA ofuscadas que intentan descargar payload.'
        },
         {
            'title': 'Publicidad Invasiva',
            'desc': 'Al navegar en sitio de proveedores salen popups raros.',
            'type': 'others',
            'risk': 'low',
            'status': 'closed',
            'target': 'http://ad-server-tracker.com',
            'vt_score': {'positives': 1, 'total': 90},
            'gemini': 'Adware / Potentially Unwanted Program (PUP).'
        },
        {
            'title': 'Actualización de Drivers',
            'desc': 'Pagina para descargar drivers de impresora.',
            'type': 'url',
            'risk': 'safe',
            'status': 'analyzed',
            'target': 'https://hp.com/support/drivers',
            'vt_score': {'positives': 0, 'total': 90},
            'gemini': 'Sitio oficial de HP. Seguro.'
        }
    ]
    
    # Generar 16 incidentes mezclando templates
    count = 0
    for i in range(16):
        template = incident_templates[i % len(incident_templates)]
        
        # Variar fechas (últimos 10 días)
        days_ago = random.randint(0, 10)
        created_at = timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        inc = Incident.objects.create(
            # title removed, not in model
            description=f"[{template['title']}] {template['desc']}",
            incident_type=template['type'],
            risk_level=template['risk'],
            status=template['status'],
            reported_by=users_objs['empleado'],
            url=template['target'] if 'http' in template['target'] else None,
            # Simular archivo si no es URL
            attached_file=None if 'http' in template['target'] else f"uploads/{template['target']}",
            analysis_result={
                'engines': [{'name': 'VirusTotal', 'positives': template['vt_score']['positives'], 'total': template['vt_score']['total']}],
                'gemini_recomendacion': template['gemini'],
                'gemini_explicacion': template['gemini'] # Para el reporte PDF
            },
            gemini_analysis=template['gemini']
        )
        
        # Hack para forzar fecha de creación pasada (auto_now_add la sobreescribe al crear, hay que updatear)
        inc.created_at = created_at
        inc.save()
        count += 1

    print(f"Generados {count} incidentes de prueba exitosamente.")
    print("\n--- SISTEMA LISTO PARA DEMO ---")

if __name__ == '__main__':
    populate()
