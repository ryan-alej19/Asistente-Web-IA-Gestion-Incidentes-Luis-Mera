import os
import django
import random
from datetime import timedelta
from django.utils import timezone

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from incidents.models import Incident

def populate():
    print("--- Generando Datos de Prueba para Taller Automotriz ---")

    # 1. Get Users
    try:
        empleado = User.objects.get(username='empleado')
    except User.DoesNotExist:
        print("El usuario 'empleado' no existe. Creando...")
        empleado = User.objects.create_user('empleado', 'empleado@tecnicontrol.com', 'empleado123')

    # 2. Define Incident Data
    # Format: (Type, Target, Risk, Status, Description)
    # The user wants realistic car workshop data.
    
    test_data = [
        # Files
        ('file', 'factura_proveedor_toyota.pdf.exe', 'CRITICAL', 'pending', 'Archivo adjunto en correo de supuesta factura.'),
        ('file', 'nomina_empleados_febrero.xlsx', 'MEDIUM', 'investigating', 'Excel con macros extrañas enviado por RRHH.'),
        ('file', 'cotizacion_frenos.pdf', 'LOW', 'resolved', 'Cotización solicitada a proveedor local.'),
        ('file', 'manual_tecnico_nissan.pdf', 'SAFE', 'resolved', 'Manual de reparación descargado de sitio oficial.'),
        ('file', 'URGENTE-verificar-pago.exe', 'CRITICAL', 'pending', 'Supuesto comprobante de pago urgente.'),
        ('file', 'inventario_repuestos_2024.docx', 'LOW', 'resolved', 'Documento de inventario interno.'),
        ('file', 'catalogo_bosch_2025.pdf.scr', 'CRITICAL', 'investigating', 'Catálogo que en realidad es un script malicioso.'),
        ('file', 'foto_daños_cliente_juan.jpg', 'SAFE', 'resolved', 'Fotos enviadas por cliente para presupuesto.'),
        ('file', 'actualizacion_sistema_taller.msi', 'HIGH', 'pending', 'Instalador no autorizado encontrado en PC recepción.'),
        
        # URLs
        ('url', 'http://repuestos-urgentes-descuento.com', 'HIGH', 'investigating', 'Link en SMS prometiendo descuentos masivos.'),
        ('url', 'https://www.toyota.com', 'SAFE', 'resolved', 'Sitio oficial de Toyota para consultas.'),
        ('url', 'actualiza-tu-cuenta-banco.com', 'CRITICAL', 'pending', 'Phishing imitando al banco del taller.'),
        ('url', 'https://www.autozone.com', 'SAFE', 'resolved', 'Consulta de precios de repuestos.'),
        ('url', 'http://ganaste-iphone-taller.xyz', 'CRITICAL', 'pending', 'Pop-up aparecido en navegador del taller.'),
        ('url', 'https://proveedores-seguros.com/login', 'LOW', 'resolved', 'Portal de proveedores habitual.'),
        ('url', 'http://192.168.1.55:8080/admin', 'MEDIUM', 'investigating', 'Intento de acceso a router interno desconocido.'),
        ('url', 'https://manuales-mecanica-gratis.net/download', 'HIGH', 'investigating', 'Sitio de descargas con mucha publicidad invasiva.'),
    ]
    
    # Ensure specific counts roughly match request
    # Request: 6 Pending, 5 In Review, 4 Resolved, 2 Closed (mapped to Resolved)
    # Total targets: 6 Pending, 5 Investigating, 6 Resolved.
    
    # Map statuses to fit request
    # My list currently has some statuses, let's override randomly to meet distribution?
    # No, let's be deterministic to look good.
    
    # Current counts in list above:
    # Pending: 5
    # Investigating: 5
    # Resolved: 6
    # SAFE usually implies Resolved/Closed.
    
    # Let's adjust to match exactly 6 Pending, 5 Review, 6 Resolved.
    # List above has 17 items.
    # I need 1 more Pending.
    test_data.append(('file', 'presupuesto_reparacion_motor.ocx', 'HIGH', 'pending', 'Archivo extraño en carpeta compartida.'))
    
    print(f"Total Incidentes a crear: {len(test_data)}")

    created_count = 0
    for i, (itype, target, risk, status, desc) in enumerate(test_data):
        # Add random time variation (last 7 days)
        days_ago = random.randint(0, 7)
        fake_date = timezone.now() - timedelta(days=days_ago)
        
        # Create
        inc = Incident(
            incident_type=itype,
            url=target if itype == 'url' else None,
            attached_file=None, # No physical file for demo DB
            description=desc,
            risk_level=risk,
            status=status,
            reported_by=empleado,
            created_at=fake_date,
            updated_at=fake_date,
            analyst_notes = f"Nota automática generado para demo: {desc}" if status != 'pending' else ""
        )
        
        # Fake file name if file type (stored in Description or we need a way to show it?
        # Model has 'attached_file' which is a FileField.
        # For 'file' type, the dashboard usually shows the filename.
        # If 'attached_file' is None, handle it.
        # Actually I can assign a dummy file object or just leave it empty.
        # But wait, usually the UI displays 'attached_file.name'. 
        # If I leave it empty, the UI might show nothing.
        # IMPORTANT: I should start the 'attached_file' with the filename string even if file doesn't exist on disk?
        # No, Django FileField expects a file. 
        # But wait, `verify_stats.py` or similar might failed if no file.
        # Let's look at frontend how it displays name.
        # It probably uses `incident.file_name` if I added it? No `models.py` has `attached_file`.
        # Frontend likely does `incident.attached_file.split('/').pop()`.
        # If I cannot easily fake file, I might use the 'description' to store filename?
        # Re-reading user: "factura_proveedor_toyota.pdf.exe".
        # I should try to hack the FileField to store a string? No.
        # I will Creates dummy empty files for these names?
        # Or I can just set `url` to the filename for now if type is file? HACK.
        # Let's check `serializers.py`.
        
        # Actually, let's look at how I implemented the "App Icon" logic in Turn 1/2... 
        # I didn't verify `models.py` deeply for file handling.
        # BUT, if `incident_type` is file, logic usually expects `attached_file`.
        
        # Strategy: Create dummy files in `media/incidents/`.
        if itype == 'file':
            # Create dummy file
            media_path = os.path.join(os.getcwd(), 'media', 'incidents')
            os.makedirs(media_path, exist_ok=True)
            file_path = os.path.join(media_path, target)
            with open(file_path, 'w') as f:
                f.write('dummy content')
            
            # Simple wrapper to assign to FileField? 
            # Actually easier: just manually set the string path in DB relative to MEDIA_ROOT
            inc.attached_file.name = f'incidents/{target}'
        
        inc.save()
        
        # Manually update created_at because auto_now_add overrides it on save()
        Incident.objects.filter(id=inc.id).update(created_at=fake_date)
        
        created_count += 1
        print(f"Creado: {target} ({risk})")

    print(f"--- Fin. {created_count} incidentes creados. ---")

if __name__ == '__main__':
    populate()
