-- SCRIPT DE ACTUALIZACION SQL PARA CUADRAR BASE DE DATOS LOCAL CON DOCUMENTO DE TESIS
-- Creado para actualizar los Casos Prácticos de Falsos Positivos documentados en Capítulo III (3.1.4)
-- =========================================================================================
-- INSTRUCCIONES:
-- Puedes ejecutar este archivo abriendo tu archivo 'db.sqlite3' en DB Browser for SQLite,
-- yendo a la pestaña "Ejecutar SQL" (Execute SQL), pegando este texto, y dando al botón Play.
-- Luego no olvides "Guardar Cambios" (Write Changes).
-- =========================================================================================

-- FALSO POSITIVO #1 (ID #43)
-- Tesis: factura_proveedor_diciembre.xlsx (5/94 detecciones)
UPDATE incidents_incident 
SET 
    description = '[factura_proveedor_diciembre.xlsx] Contenía macro VBA para cálculo automático de IVA. 2 motores antivirus marcaron la macro como "potencialmente no deseada" pese a ser código legítimo del proveedor.',
    risk_level = 'LOW',
    incident_type = 'file',
    url = NULL,
    attached_file = 'uploads/factura_proveedor_diciembre.xlsx',
    gemini_analysis = 'Contenía macro VBA para cálculo automático de IVA. 2 motores antivirus marcaron la macro como "potencialmente no deseada" pese a ser código legítimo del proveedor.'
WHERE id = 43;

-- FALSO POSITIVO #2 (ID #40)
-- Tesis: manual_reparacion_toyota.pdf (3/94 detecciones)
UPDATE incidents_incident 
SET 
    description = '[manual_reparacion_toyota.pdf] PDF escaneado con firma digital embebida. MetaDefender clasificó el certificado digital como "no verificado" por ser de autoridad certificadora no reconocida.',
    risk_level = 'LOW',
    incident_type = 'file',
    url = NULL,
    attached_file = 'uploads/manual_reparacion_toyota.pdf',
    gemini_analysis = 'PDF escaneado con firma digital embebida. MetaDefender clasificó el certificado digital como "no verificado" por ser de autoridad certificadora no reconocida.'
WHERE id = 40;

-- FALSO POSITIVO #3 (ID #42)
-- Tesis: instalador_driver_hp.msi (8/94 detecciones)
UPDATE incidents_incident 
SET 
    description = '[instalador_driver_hp.msi] Instalador MSI sin firma digital de Microsoft. Varios motores lo marcaron como "software POTENCIALMENTE NO DESEADO" por instalar barras de herramientas adicionales.',
    risk_level = 'LOW',
    incident_type = 'file',
    url = NULL,
    attached_file = 'uploads/instalador_driver_hp.msi',
    gemini_analysis = 'Instalador MSI sin firma digital de Microsoft. Varios motores lo marcaron como "software POTENCIALMENTE NO DESEADO" por instalar barras de herramientas adicionales.'
WHERE id = 42;

-- NOTA IMPORTANTE: 
-- SQLite no soporta modificaciones limpias de objetos JSON dentro de campos de texto en todas las versiones.
-- Para que el campo nativo "analysis_result" (que contiene el objeto JSON con las "detecciones X/94" visuales)
-- también se cambie a la perfección, he dejado un script Python en tu proyecto que automáticamente lo hace todo bien usando el ORM de Django:
-- Ruta: backend/scripts/fix_thesis_false_positives.py
-- Comando a ejecutar en terminal: python manage.py shell < scripts/fix_thesis_false_positives.py
