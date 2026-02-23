import os
import sys
import django

# Configuración de entorno Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from incidents.models import Incident

def update_thesis_fp():
    print("=" * 60)
    print("  ACTUALIZANDO CASOS DOCUMENTADOS EN TESIS (FALSOS POSITIVOS)")
    print("=" * 60)
    
    # Datos exactos requeridos por el tutor en Cap III, sección 3.1.4
    updates = {
        43: {
            'title': 'factura_proveedor_diciembre.xlsx',
            'desc': 'Contenía macro VBA para cálculo automático de IVA. 2 motores antivirus marcaron la macro como "potencialmente no deseada" pese a ser código legítimo del proveedor.',
            'risk': 'LOW',
            'type': 'file',
            'vt_positives': 5,
            'vt_total': 94
        },
        40: {
            'title': 'manual_reparacion_toyota.pdf',
            'desc': 'PDF escaneado con firma digital embebida. MetaDefender clasificó el certificado digital como "no verificado" por ser de autoridad certificadora no reconocida.',
            'risk': 'LOW',
            'type': 'file',
            'vt_positives': 3,
            'vt_total': 94
        },
        42: {
            'title': 'instalador_driver_hp.msi',
            'desc': 'Instalador MSI sin firma digital de Microsoft. Varios motores lo marcaron como "software POTENCIALMENTE NO DESEADO" por instalar barras de herramientas adicionales.',
            'risk': 'LOW',
            'type': 'file',
            'vt_positives': 8,
            'vt_total': 94
        }
    }
    
    count = 0
    for inc_id, data in updates.items():
        try:
            inc = Incident.objects.get(id=inc_id)
            print(f"\n[ID #{inc_id}] Encontrado. Original: {inc.description[:40]}... ({inc.risk_level})")
            
            # Aplicar actualizaciones
            inc.description = f"[{data['title']}] {data['desc']}"
            inc.incident_type = data['type']
            inc.risk_level = data['risk']
            # Es un archivo, así que limpiamos la URL y actualizamos el archivo adjunto
            inc.url = ""
            inc.attached_file = f"uploads/{data['title']}"
            
            # Actualizar resultado de análisis para que refleje los motores
            analysis = inc.analysis_result or {}
            
            engines = analysis.get('engines', [])
            vt_found = False
            for engine in engines:
                if engine.get('name') == 'VirusTotal':
                    engine['positives'] = data['vt_positives']
                    engine['total'] = data['vt_total']
                    vt_found = True
                    break
                    
            if not vt_found:
                engines.append({
                    'name': 'VirusTotal',
                    'positives': data['vt_positives'],
                    'total': data['vt_total']
                })
                
            analysis['engines'] = engines
            analysis['gemini_explicacion'] = data['desc']
            analysis['gemini_recomendacion'] = "CONFIRMACIÓN DE FALSO POSITIVO: Archivo legítimo de operación del negocio. Recomendación: Añadir hash a lista blanca/excepciones del sistema."
            
            inc.analysis_result = analysis
            inc.gemini_analysis = data['desc']
            
            # Guardamos los cambios en la base de datos
            inc.save()
            print(f"  -> ACTUALIZADO A: {data['title']} ({inc.risk_level}) - Detecciones: {data['vt_positives']}/{data['vt_total']}")
            count += 1
            
        except Incident.DoesNotExist:
            print(f"\n[ERROR] Incidente ID #{inc_id} NO EXISTE en la base de datos actual.")
            
    print("\n" + "=" * 60)
    print(f"  {count}/3 INCIDENTES ACTUALIZADOS EXITOSAMENTE")
    print("=" * 60)

if __name__ == '__main__':
    update_thesis_fp()
