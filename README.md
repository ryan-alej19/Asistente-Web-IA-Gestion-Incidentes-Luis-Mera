# 🔒 Asistente Web con IA para Gestión de Incidentes de Ciberseguridad

**Tesis de Tecnología Superior en Desarrollo de Software**  
**Autor:** Ryan Gallegos Mera  
**Universidad:** PUCESI - Quito, Ecuador  
**Empresa:** Talleres Luis Mera  
**Estado:** EN DESARROLLO ⚙️ (43% completado)  

---

## 📋 Descripción General

Aplicación web inteligente que permite a empleados de pequeñas empresas **reportar incidentes de ciberseguridad** de forma simple e intuitiva. El sistema analiza automáticamente cada reporte utilizando **inteligencia artificial local** para asignar un nivel de severidad y facilita la gestión centralizada de amenazas.

### 🎯 Objetivo

Diseñar e implementar un sistema web que registre, clasifique y analice incidentes de ciberseguridad automáticamente, mejorando la **capacidad de respuesta organizacional** en pequeñas empresas ecuatorianas que carecen de recursos especializados.

### ✨ Características Principales

✅ **Portal de Empleados:** Interfaz simple para reportar incidentes  
✅ **Dashboard Administrativo:** Visualización de estadísticas en tiempo real  
✅ **Análisis Automático con IA:** Clasificación de amenazas por severidad  
✅ **Base de Datos Centralizada:** Almacenamiento de todos los incidentes  
✅ **API REST:** Endpoints para integración futura  
✅ **Documentación Completa:** Guías para desarrollo y despliegue  

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Versión |
|-----------|-----------|----------|
| **Backend** | Django + DRF | 4.x + 3.x |
| **Frontend** | React | 18.x |
| **Database** | PostgreSQL (prod) / SQLite (dev) | 13+ / 3.x |
| **IA** | Python puro (reglas + scoring) | - |
| **Lenguaje Backend** | Python | 3.9+ |
| **Lenguaje Frontend** | JavaScript/JSX | ES6+ |
| **Contenedorización** | Docker | - |

---

## 🚀 Inicio Rápido (5 minutos)

### Requisitos Previos

```bash
# Verificar que tienes instalado
python --version          # 3.9+
npm --version             # 6.0+
git --version             # 2.0+
```

### Backend (Django)

```bash
# 1. Navegar a carpeta backend
cd backend

# 2. Crear ambiente virtual
python -m venv venv

# 3. Activar (Windows/Git Bash)
source venv/Scripts/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Correr servidor
python manage.py runserver

# ✅ Acceso: http://localhost:8000/api/incidents/
```

### Frontend (React)

```bash
# 1. Navegar a carpeta frontend (EN OTRA TERMINAL)
cd frontend

# 2. Instalar dependencias
npm install

# 3. Crear archivo .env
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# 4. Correr servidor
npm start

# ✅ Se abre: http://localhost:3000
```

### ✅ Verificación

```bash
# Prueba que backend responde
curl http://localhost:8000/api/incidents/

# Debe retornar: [] (lista vacía)

# En navegador:
# Frontend: http://localhost:3000 ✅
# Backend:  http://localhost:8000 ✅
```

---

## 📁 Estructura del Proyecto

```
tesis-asistente-ciberseguridad/
├── backend/                  # Django - API REST
│   ├── config/              # Configuración Django
│   ├── api/                 # App principal
│   │   ├── models.py        # ✅ Modelo Incident
│   │   ├── views.py         # ⚙️ ViewSets (en progreso)
│   │   ├── serializers.py   # ✅ JSON serialization
│   │   └── urls.py          # ✅ Rutas API
│   ├── ia_classifier/       # ❌ IA Local (próximo paso)
│   ├── requirements.txt      # Dependencias Python
│   └── manage.py
│
├── frontend/                 # React - Interfaz Usuario
│   ├── src/
│   │   ├── components/      # ✅ ReportForm, Dashboard
│   │   ├── services/        # ✅ api.js (HTTP client)
│   │   └── App.jsx          # ⚙️ Componente principal
│   ├── package.json
│   └── .env                 # Variables de entorno
│
├── docker/                   # ❌ Docker (próximo paso)
├── README.md                 # Este archivo
├── CONTEXTO_PROYECTO_ACTUALIZADO.md   # Contexto completo
└── WINDOWS_SETUP_GUIA_RAPIDA.md       # Guía para Windows
```

---

## 📚 Documentación

### Para desarrollo:

| Documento | Contenido |
|-----------|----------|
| **CONTEXTO_PROYECTO_ACTUALIZADO.md** | Estado actual, cronograma, checklist defensa |
| **WINDOWS_SETUP_GUIA_RAPIDA.md** | Guía completa para Windows + Git + VS Code |
| **TESTING_FASE1.md** | Plan de testing y casos de prueba |

### Tutoriales útiles:

- [Django REST Framework Docs](https://www.django-rest-framework.org/)
- [React Official Guide](https://react.dev/)
- [Docker Getting Started](https://docs.docker.com/get-started/)

---

## 🧠 Cómo Funciona la IA Local

### Modelo de Clasificación

No usa Machine Learning, sino **reglas basadas en palabras clave** explicables:

```python
# Clasificador simple pero efectivo
if "phishing" in description and detecta palabras clave:
    severity = "MEDIO" (mínimo)
    
if "malware" in description:
    severity = "ALTO" (mínimo)
    
if "acceso no autorizado" in description:
    severity = "MEDIO" (mínimo)

# Score aumenta con más coincidencias
if score >= 4: severity = "CRÍTICO"
if score >= 3: severity = "ALTO"
if score >= 1: severity = "MEDIO"
else:         severity = "BAJO"
```

### Severidades

| Nivel | Confianza | Acción |
|-------|-----------|--------|
| **CRÍTICO** | 0.95 | Respuesta inmediata requerida |
| **ALTO** | 0.80 | Investigación prioritaria |
| **MEDIO** | 0.60 | Seguimiento estándar |
| **BAJO** | 0.30 | Monitoreo |

---

## 📊 API Endpoints

### Incidentes

```
GET    /api/incidents/              # Listar incidentes
POST   /api/incidents/              # Crear incidente (con IA)
GET    /api/incidents/{id}/         # Detalle de incidente
PATCH  /api/incidents/{id}/         # Actualizar estado
DELETE /api/incidents/{id}/         # Eliminar incidente
```

### Estadísticas

```
GET    /api/stats/                  # Estadísticas globales
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
source venv/Scripts/activate
python manage.py test
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🐳 Docker (Próxima Fase)

```bash
# Construir imágenes
docker-compose build

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

---

## 📅 Estado Actual (Diciembre 2025)

| Componente | Avance | Estado |
|-----------|--------|--------|
| Frontend | 70% | ⚙️ En progreso - Integraciones finales |
| Backend | 65% | ⚙️ En progreso - Refinamientos |
| IA Clasificador | 40% | ❌ **PRIORIDAD:** Implementar esta semana |
| Testing | 10% | ❌ Pendiente |
| Docker | 0% | ⏳ Última semana antes de defensa |
| **GENERAL** | **43%** | **Defensa en 4-8 semanas** |

**Próximo paso:** ⚡ Implementar `classifier.py` y integrar con backend

---

## 👥 Contribuidores

- **Ryan Gallegos Mera** - Desarrollador Principal
- **Tutor PUCESI** - Guía académica
- **Talleres Luis Mera** - Empresa colaboradora

---

## 📞 Contacto

**Email:** ryangallegosmera1@gmail.com  
**Teléfono:** +593 992559394  
**Ubicación:** Quito, Ecuador  
**Repositorio:** [GitHub](https://github.com/ryan-alej19/tesis-asistente-ciberseguridad)  

---

## 📄 Licencia

Este proyecto es de código abierto con fines académicos.

---

## 🎓 Referencias Académicas

- Fernández de Arroyabe, J. C., et al. (2024). *Cybersecurity resilience in SMEs*
- Mohamed, N. (2025). *AI and Machine Learning in Cybersecurity*
- Delgado Pilozo, R., et al. (2025). *Estrategias de ciberseguridad en PYMES*

---

## ⚡ Quick Help

### ¿Dónde empezar?

1. **Leer:** `CONTEXTO_PROYECTO_ACTUALIZADO.md` (comprende el proyecto)
2. **Setup:** `WINDOWS_SETUP_GUIA_RAPIDA.md` (configura entorno)
3. **Codificar:** Comienza con `ia_classifier.py`
4. **Probar:** Ejecuta tests localmente
5. **Documentar:** Actualiza README mientras avanzas

### Comandos frecuentes

```bash
# Backend
cd backend && source venv/Scripts/activate && python manage.py runserver

# Frontend
cd frontend && npm start

# Tests
python manage.py test        # Backend
npm test                      # Frontend

# Git
git add . && git commit -m "feat: [descripción]" && git push
```

### Solucionar problemas

- Puerto 8000 ocupado: `python manage.py runserver 8001`
- Puerto 3000 ocupado: `npm start -- --port 3001`
- Venv no activa: `source venv/Scripts/activate`
- Dependencias faltantes: `pip install -r requirements.txt`

---

**Última actualización:** 26 de Diciembre, 2025  
**Próxima revisión:** Al completar fase IA (máximo 1 semana)  
**Estado de defensa:** ✅ En preparación

---

### 📌 Importante

⚠️ **NO hagas push de:**
- `backend/venv/` (ambiente virtual)
- `frontend/node_modules/` (dependencias npm)
- `backend/db.sqlite3` (base de datos local)
- `frontend/.env` (variables sensibles)
- `__pycache__/` (archivos compilados Python)

✅ **Verifica que tu `.gitignore` contiene estos patrones**

---

🚀 **¡A por la defensa!** Tú puedes lograrlo. 💪
