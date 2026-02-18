
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from incidents.models import Incident
from django.utils import timezone
import random
import json
from datetime import timedelta

class Command(BaseCommand):
    help = 'Poblar base de datos con datos controlados para tesis'

    def handle(self, *args, **kwargs):
        self.stdout.write("--- INICIANDO SEEDING DE DATOS (MODO TESIS) ---")

        # 1. Limpieza
        self.stdout.write("Limpiando incidentes existentes...")
        Incident.objects.all().delete()
        
        # RESETEAR CONTADOR DE IDs (SQLite)
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name = 'incidents_incident'")
            self.stdout.write("Contador de IDs reiniciado a 0.")
        
        # Obtener usuario reportador
        try:
            empleado = User.objects.get(username='empleado')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("Usuario 'empleado' no encontrado. Creando fallback..."))
            empleado = User.objects.create_user('empleado', 'emp@test.com', 'empleado123')

        # 2. Datos Hardcodeados
        urls_data = [
            ("http://malware.testing.google.test/testing/malware/", "CRITICAL"),
            ("http://amtso.eicar.org/PotentiallyUnwanted.exe", "CRITICAL"),
            ("http://phishing-test.com/login", "HIGH"),
            ("http://testsafebrowsing.appspot.com/s/phishing.html", "CRITICAL"),
            ("http://testsafebrowsing.appspot.com/s/malware.html", "CRITICAL"),
            ("https://www.google.com", "LOW"),
            ("https://www.pucesi.edu.ec", "LOW"),
            ("https://www.facebook.com", "LOW"),
            ("http://malicious-url-test.com/spam", "HIGH"),
            ("http://fake-bank-login.xyz/account", "CRITICAL"),
            ("https://www.youtube.com", "LOW"),
            ("http://suspicious-download.info/file.exe", "HIGH"),
            ("https://www.wikipedia.org", "LOW"),
            ("http://sketchy-pharmacy.online/buy", "MEDIUM"),
        ]

        files_data = [
            ("eicar.com", "CRITICAL"),
            ("test_malware.exe", "CRITICAL"),
            ("documento_normal.pdf", "LOW"),
            ("factura_sospechosa.xlsx", "MEDIUM"),
            ("instalador_crackeado.exe", "HIGH"),
            ("imagen_vacaciones.jpg", "LOW"),
            ("keylogger_test.exe", "CRITICAL"),
            ("contrato_cliente.docx", "LOW"),
            ("supuesto_antivirus.exe", "HIGH"),
            ("backup_sistema.zip", "LOW"),
        ]

        # Combinar en una sola lista de diccionarios
        all_items = []
        for url, risk in urls_data:
            all_items.append({'type': 'url', 'target': url, 'risk': risk})
        for fname, risk in files_data:
            all_items.append({'type': 'file', 'target': fname, 'risk': risk})
            
        total_items = len(all_items) # 24
        
        # 3. Distribución de Estados (Total 24)
        # 14 Resolved, 6 In Review, 4 Pending
        statuses = ['resolved'] * 14 + ['investigating'] * 6 + ['pending'] * 4
        random.shuffle(statuses) # Mezclar estados

        # 4. Distribución de Fechas (8 semanas)
        # Semanas 1-2 (Hace 43-56 dias): 4 incidentes
        # Semanas 3-4 (Hace 29-42 dias): 6 incidentes
        # Semanas 5-6 (Hace 15-28 dias): 7 incidentes
        # Semanas 7-8 (Hace 0-14 dias): 7 incidentes (Total 24)
        
        date_ranges = []
        now = timezone.now()
        
        # Range 1: 4 items
        for _ in range(4):
            days = random.randint(43, 56)
            date_ranges.append(now - timedelta(days=days, hours=random.randint(0, 23)))
            
        # Range 2: 6 items
        for _ in range(6):
            days = random.randint(29, 42)
            date_ranges.append(now - timedelta(days=days, hours=random.randint(0, 23)))
            
        # Range 3: 7 items
        for _ in range(7):
            days = random.randint(15, 28)
            date_ranges.append(now - timedelta(days=days, hours=random.randint(0, 23)))
            
        # Range 4: 7 items (Ajuste para sumar 24: 4+6+7+7 = 24)
        for _ in range(7):
            days = random.randint(0, 14)
            date_ranges.append(now - timedelta(days=days, hours=random.randint(0, 23)))
            
        date_ranges.sort() # Ordenar cronológicamente para asignar
        
        # Asignar aleatoriamente los items a las fechas/estados
        # Ojo: Para que se vea REALISTA, los 'Pending' deberían ser los más recientes?
        # El usuario pidió "Asigna aleatoriamente pero respetando estos totales".
        # Vamos a mezclar los items para que no estén todos los URLs primero y luego archivos.
        random.shuffle(all_items)
        
        # Estrategia:
        # Asignar fechas (ya ordenadas del pasado al presente) a los items mezclados?
        # Mejor: Asignar fechas a los items.
        # Luego los estados.
        # Vamos a asignar estados a los indices basados en la fecha para realismo?
        # NO, el usuario pide "aleatoriamente". Cumplamos eso estrictamente para no complicar.
        
        for i, item in enumerate(all_items):
            item['date'] = date_ranges[i]
            item['status'] = statuses[i]

        # Generar Incidentes
        self.stdout.write(f"Generando {total_items} incidentes...")
        
        for item in all_items:
            # Mock Analysis Result
            risk = item['risk']
            mock_result = {}
            vt_dummy = {}
            score = 0
            
            if risk == 'CRITICAL':
                vt_dummy = {'positives': 55, 'total': 90}
                mock_result = {"engine": "VirusTotal", "verdict": "Malicious", "detections": "55/90"}
                
            elif risk == 'HIGH':
                vt_dummy = {'positives': 20, 'total': 90}
                mock_result = {"engine": "Heuristic", "verdict": "Suspicious", "reason": "Phishing patterns"}
                
            elif risk == 'MEDIUM':
                vt_dummy = {'positives': 5, 'total': 90}
                mock_result = {"engine": "MetaDefender", "verdict": "Warning", "reason": "Unknown signature"}
                
            elif risk == 'LOW':
                vt_dummy = {'positives': 0, 'total': 90}
                mock_result = {"engine": "Gemini AI", "verdict": "Safe", "reason": "Legitimate resource"}

            # Descripción basada en target
            desc = f"Análisis automático para {item['target']}"
            
            inc = Incident(
                incident_type=item['type'],
                url=item['target'] if item['type'] == 'url' else None,
                attached_file=None, # Solo nombre simulado
                description=desc,
                risk_level=risk,
                status=item['status'],
                reported_by=empleado,
                virustotal_result=vt_dummy,
                analysis_result=mock_result, # Campo JSON genérico
                created_at=item['date'],
                updated_at=item['date']
            )
            
            # Hack para nombre de archivo
            if item['type'] == 'file':
                inc.attached_file.name = f"incidents/{item['target']}"
                
            inc.save()
            
            # Forzar fecha
            Incident.objects.filter(id=inc.id).update(created_at=item['date'], updated_at=item['date'])
            
            self.stdout.write(f"Creado: {item['target']} | {risk} | {item['status']}")

        self.stdout.write(self.style.SUCCESS("✅ PROCESO COMPLETADO. Base de datos lista para tesis."))
