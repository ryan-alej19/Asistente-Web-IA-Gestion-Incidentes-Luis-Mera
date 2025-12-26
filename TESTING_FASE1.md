# 🧪 TESTING FASE 1 - Persistencia Real de Datos

## ✅ CHECKLIST DE VERIFICACIÓN

Ante de continuar, verifica que:

- [ ] Backend corre: `python manage.py runserver`
- [ ] Frontend corre: `npm start`
- [ ] Ambos en terminales separadas
- [ ] No hay errores en consola

---

## 🔄 PRUEBAS CON POSTMAN

### 1️⃣ **Crear Incidente (POST)**

**URL:** `http://127.0.0.1:8000/api/incidents/`
**Método:** POST
**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "description": "Recibí un email del CEO pidiendo transferencia urgente al banco",
  "threat_type": "PHISHING",
  "criticality": "ALTO",
  "resolved": false
}
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "description": "Recibí un email del CEO pidiendo transferencia urgente al banco",
  "threat_type": "PHISHING",
  "criticality": "ALTO",
  "ai_recommendation": "",
  "created_at": "2025-12-24T04:15:00Z",
  "resolved": false
}
```

✅ **Si ves el `"id": 1`, significa que se guardó en BD!**

---

### 2️⃣ **Listar Incidentes (GET)**

**URL:** `http://127.0.0.1:8000/api/incidents/`
**Método:** GET

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "description": "Recibí un email del CEO...",
    "threat_type": "PHISHING",
    "criticality": "ALTO",
    "ai_recommendation": "",
    "created_at": "2025-12-24T04:15:00Z",
    "resolved": false
  }
]
```

✅ **Si ves el incidente creado, el GET funciona!**

---

### 3️⃣ **Analizar Incidente (POST)**

**URL:** `http://127.0.0.1:8000/api/incidents/1/analyze/`
**Método:** POST
**Body:** {} (vacío)

**Respuesta esperada:**
```json
{
  "success": true,
  "incident_id": 1,
  "analysis": {
    "threat_type": "PHISHING",
    "criticality": "ALTO",
    "confidence": 0.92,
    "recommendation": "No haga clic ni responda. Reporte a TI inmediatamente.",
    "technical_details": "Detectado patrón de probable phishing o intento fraudulento."
  }
}
```

✅ **Si recibe análisis, la lógica IA funciona!**

---

### 4️⃣ **Actualizar Incidente (PUT)**

**URL:** `http://127.0.0.1:8000/api/incidents/1/`
**Método:** PUT
**Body:**
```json
{
  "description": "Recibí un email del CEO pidiendo transferencia urgente al banco",
  "threat_type": "PHISHING",
  "criticality": "ALTO",
  "resolved": true
}
```

**Respuesta esperada:** El incidente actualizado con `"resolved": true`

✅ **Si se actualiza, el PUT funciona!**

---

### 5️⃣ **Estadísticas (GET)**

**URL:** `http://127.0.0.1:8000/api/incidents/stats/`
**Método:** GET

**Respuesta esperada:**
```json
{
  "total_incidents": 1,
  "critical_incidents": 0,
  "resolved_incidents": 1,
  "pending_incidents": 0,
  "incidents_by_type": {
    "PHISHING": 1
  }
}
```

✅ **Si ves conteos reales de BD, el stats funciona!**

---

## 🖥️ PRUEBAS EN FRONTEND

### 6️⃣ **Portal Empleado - Crear Incidente**

1. Abre `http://localhost:3000`
2. Haz clic en **"Portal Empleado"**
3. Escribe una descripción en el textarea:
   ```
   Se descargó un archivo sospechoso que ralentizó mi equipo
   ```
4. Haz clic en **"Analizar Amenaza Ahora"**
5. Espera resultado

**Resultado esperado:**
- Tipo: **MALWARE**
- Criticidad: **CRÍTICO**
- Confianza: **88%**
- Recomendación: "Aísle su equipo y contacte soporte técnico de inmediato."

✅ **Si ves resultado correcto, frontend→backend→BD funciona!**

---

### 7️⃣ **Centro SOC - Ver Incidentes**

1. En `http://localhost:3000`, haz clic en **"Centro de Comando SOC"**
2. Mira la tabla "Registro Completo de Incidentes"
3. Deberías ver los incidentes que creaste

**Resultado esperado:**
- Tabla con incidentes reales de BD
- Botones "Resolver" y "Eliminar" funcionales
- Gráficos actualizados si hay múltiples incidentes

✅ **Si ves tabla con datos reales, dashboard funciona!**

---

## 🐛 TROUBLESHOOTING

### Error: "Cannot POST /api/incidents/"

**Solución:**
```bash
# Verifica que backend está corriendo
cd backend
python manage.py runserver

# Verifica que CORS está habilitado en settings.py
# Debe tener: CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]
```

---

### Error: "Network Error"

**Solución:**
```bash
# Backend debe estar en puerto 8000
http://127.0.0.1:8000/api/incidents/

# Frontend debe estar en puerto 3000
http://localhost:3000
```

---

### Error: "ModuleNotFoundError: No module named 'rest_framework'"

**Solución:**
```bash
cd backend
pip install djangorestframework
python manage.py runserver
```

---

### Error: "Database locked"

**Solución:**
```bash
# SQLite tiene problemas con acceso concurrente
# Solución: reinicia el backend

cd backend
# Ctrl+C para detener
python manage.py runserver
```

---

## ✨ SEÑALES DE ÉXITO

| Característica | Status |
|---|---|
| Backend corre sin errores | ✅ |
| Frontend corre sin errores | ✅ |
| POST /api/incidents/ crea en BD | ✅ |
| GET /api/incidents/ devuelve datos reales | ✅ |
| POST /api/incidents/{id}/analyze/ funciona | ✅ |
| Frontend muestra incidentes de BD | ✅ |
| Dashboard carga estadísticas reales | ✅ |
| Puedes resolver/eliminar incidentes | ✅ |

**Si todos tienen ✅, FASE 1 está completa!**

---

## 📊 MÉTRICA: Progreso

- **Antes:** 20% (solo estructura)
- **Después:** 35% (CRUD funcional con BD real)
- **Ganancia:** +15%

---

## 🎯 Próximo paso después de validar:

```bash
cd backend
git add .
git commit -m "Feat: FASE 1 - Persistencia real de datos CRUD completo"
git push origin main
```

---

**Última actualización:** 24 de Diciembre de 2025  
**Estado:** 🟢 LISTO PARA TESTING  
**Tiempo estimado de testing:** 15-20 minutos
