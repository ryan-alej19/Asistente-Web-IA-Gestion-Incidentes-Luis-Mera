<div align="center">

<img src="https://www.pucesi.edu.ec/web/wp-content/uploads/2019/04/logo-PUCE-SI.png" alt="PUCE TEC Logo" width="180"/>

<br/>

# 🛡️ ASISTENTE WEB CON INTELIGENCIA ARTIFICIAL PARA LA GESTIÓN DE INCIDENTES DE CIBERSEGURIDAD EN TALLERES LUIS MERA

<p align="center">
  <img src="https://img.shields.io/badge/Estado-Completado-brightgreen?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Versión-1.0.3_Enterprise-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Institución-PUCE_TEC-navy?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Año-2026-orange?style=for-the-badge" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.1.4-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Containerizado-2496ED?style=for-the-badge&logo=docker&logoColor=white" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/VirusTotal-API_v2-394EFF?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white" />
  <img src="https://img.shields.io/badge/MetaDefender-Cloud_v4-FF6B35?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Safe_Browsing-Google_v4-34A853?style=for-the-badge&logo=google" />
</p>

---

> **Trabajo de Integración Curricular** — Tecnología Superior en Desarrollo de Software  
> **Pontificia Universidad Católica del Ecuador — Sede Ibarra (PUCE TEC)**  
> **Cliente:** Talleres Luis Mera — Ibarra, Ecuador | **Año:** 2026

</div>

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Funcionalidades](#-funcionalidades)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación Local](#-instalación-local)
- [Instalación con Docker](#-instalación-con-docker)
- [Variables de Entorno](#-variables-de-entorno)
- [Usuarios de Prueba](#-usuarios-de-prueba)
- [APIs Integradas](#-apis-integradas)
- [Métricas del Sistema](#-métricas-del-sistema)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Autor](#-autor)

---

## 🎯 Descripción del Proyecto

El **Asistente Web con IA para Gestión de Incidentes de Ciberseguridad** es una plataforma web desarrollada como solución tecnológica para **Talleres Luis Mera**, una microempresa automotriz ubicada en Ibarra, Ecuador.

El sistema automatiza el análisis de amenazas cibernéticas mediante la integración de **cuatro motores de seguridad externos** y **Inteligencia Artificial Generativa (Google Gemini 2.5 Flash)**, permitiendo que personal no técnico pueda identificar y reportar incidentes de seguridad de manera efectiva.

### 🎯 Objetivos del Sistema

| Objetivo | Descripción |
|----------|-------------|
| **Automatización** | Análisis automático de archivos y URLs sospechosas en <12 segundos |
| **Inteligencia Explicable** | Gemini AI traduce resultados técnicos a lenguaje simple |
| **Gestión Centralizada** | Flujo completo de incidentes: reporte → revisión → resolución |
| **Control de Acceso** | Tres roles diferenciados con permisos específicos |
| **Costo Cero** | Opera 100% en capas gratuitas de todas las APIs |

### ❗ Lo que el sistema NO es
> Este sistema **NO es** un IDS, IPS, antivirus ni herramienta de monitoreo de tráfico de red.  
> Es un **asistente de apoyo a la toma de decisiones** orientado a PYMES, alineado con estándares reconocidos.

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Navegador Web)                   │
│              React 18 + Tailwind CSS + TailwindUI            │
│          Lucide React (Iconos) + Framer Motion (Animaciones) │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTPS / JWT Auth
┌──────────────────────▼──────────────────────────────────────┐
│                  SERVIDOR (Django REST API)                   │
│                  Django 5.1.4 + DRF + SQLite                 │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Empleado   │  │   Analista   │  │ Administrador    │  │
│  │   Module     │  │   Module     │  │ Module           │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Motor de Análisis Multi-API              │   │
│  │  Cache 24h │ Failover Auto │ Clasificador Heurístico  │   │
│  └─────────────────────────────────────────────────────┘   │
└──────┬────────────┬──────────────┬─────────────┬───────────┘
       │            │              │             │
┌──────▼──┐  ┌──────▼──┐  ┌───────▼──┐  ┌──────▼──────┐
│VirusTotal│  │MetaDef. │  │Google GSB│  │Gemini 2.5   │
│  API v2  │  │Cloud v4 │  │   API v4 │  │Flash AI     │
└──────────┘  └─────────┘  └──────────┘  └─────────────┘
```

---

## ✨ Funcionalidades

### 👤 Panel de Empleado
- ✅ Análisis de **URLs sospechosas** con 4 motores simultáneos
- ✅ Análisis de **archivos** (exe, pdf, docx, zip, etc.)
- ✅ Política **Zero Trust** para archivos ZIP cifrados
- ✅ **Semáforo de riesgo** visual (CRÍTICO / ALTO / MEDIO / BAJO / SEGURO)
- ✅ **Explicación en lenguaje simple** generada por Gemini AI
- ✅ Creación de reportes de incidentes
- ✅ Historial personal de incidentes reportados
- ✅ Sistema de **caché 24 horas** para análisis repetidos

### 🔍 Panel de Analista
- ✅ **Dashboard estadístico** con 3 gráficos (Recharts)
- ✅ Vista de **todos los incidentes** de todos los usuarios
- ✅ **Filtros avanzados** por tipo, riesgo, estado y búsqueda
- ✅ **Gestión de estados**: Pendiente → En Revisión → Resuelto → Cerrado
- ✅ Vista completa de **análisis técnico** por incidente
- ✅ **Notas internas** visibles solo para analistas
- ✅ Historial de cambios de estado

### 👑 Panel de Administrador
- ✅ Todo lo del Analista
- ✅ **Gestión de usuarios** registrados
- ✅ **Activar/Desactivar** cuentas de usuario
- ✅ **Cambio de roles** entre niveles

### 🤖 Motor de IA (Backend)
- ✅ **Clasificador heurístico** (F1-Score: 90.8%)
- ✅ **Failover automático** ante caídas de APIs
- ✅ **Cache Django** reduce 65% de consultas externas
- ✅ **Gemini Singleton** con fallback garantizado
- ✅ Detección de typosquatting y doble extensión

---

## 🛠️ Stack Tecnológico

### Backend
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| Python | 3.11 | Lenguaje base |
| Django | 5.1.4 | Framework web |
| Django REST Framework | 3.x | API REST |
| SQLite | 3.x | Base de datos |
| JWT (SimpleJWT) | Latest | Autenticación |
| Django Cache Framework | Built-in | Sistema de caché |
| Gunicorn | Latest | Servidor WSGI (producción) |
| ReportLab | Latest | Generación de PDFs |

### Frontend
| Tecnología | Versión | Uso |
|-----------|---------|-----|
| React | 18 | Biblioteca UI |
| Tailwind CSS | 3.x | Estilos |
| TailwindUI | Latest | Componentes UI |
| Lucide React | 0.263.1 | Iconografía |
| Framer Motion | Latest | Animaciones |
| Recharts | Latest | Gráficos estadísticos |
| Axios | Latest | Peticiones HTTP |

### APIs Externas
| API | Plan | Uso |
|-----|------|-----|
| VirusTotal API v2 | Gratuito | Análisis multi-antivirus |
| MetaDefender Cloud v4 | Gratuito | Análisis multi-motor |
| Google Safe Browsing v4 | Gratuito | Listas negras de URLs |
| Google Gemini 2.5 Flash | Gratuito | Análisis IA explicable |

### DevOps
| Tecnología | Uso |
|-----------|-----|
| Docker | Contenedorización |
| Docker Compose | Orquestación local |
| Render.com | Despliegue en la nube |
| GitHub | Control de versiones |

---

## 📁 Estructura del Proyecto

```
asistente-ciberseguridad-talleres-luis-mera/
│
├── 📁 backend/
│   ├── 📁 config/              # Configuración Django
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── 📁 users/               # Módulo de usuarios y roles
│   │   ├── models.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── 📁 incidents/           # Módulo de incidentes
│   │   ├── models.py           # Incident, IncidentNote
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   ├── 📁 analysis/            # Motor de análisis multi-API
│   │   ├── virustotal.py
│   │   ├── metadefender.py
│   │   ├── safe_browsing.py
│   │   ├── gemini_service.py   # Singleton + fallback
│   │   └── heuristic.py        # Clasificador heurístico
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 pages/
│   │   │   ├── Login.jsx
│   │   │   ├── EmployeeDashboard.jsx
│   │   │   ├── AnalystDashboard.jsx
│   │   │   └── AdminDashboard.jsx
│   │   ├── 📁 components/
│   │   │   └── 📁 analyst/
│   │   │       ├── IncidentDetailModal.jsx
│   │   │       ├── ChangeStateModal.jsx
│   │   │       └── NotesSection.jsx
│   │   └── 📁 config/
│   │       └── api.js
│   ├── Dockerfile
│   └── .env.production
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🚀 Instalación Local

### Prerequisitos
- Python 3.11+
- Node.js 18+
- Git

### Backend

```bash
# 1. Clonar repositorio
git clone https://github.com/ryan-alej19/asistente-ciberseguridad-talleres-luis-mera.git
cd asistente-ciberseguridad-talleres-luis-mera

# 2. Crear entorno virtual
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus claves de API

# 5. Migrar base de datos
python manage.py migrate

# 6. Iniciar servidor
python manage.py runserver
```

### Frontend

```bash
# En otra terminal
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm start
```

✅ **Backend:** `http://localhost:8000`  
✅ **Frontend:** `http://localhost:3000`

---

## 🐳 Instalación con Docker

### Prerequisitos
- Docker Desktop instalado y corriendo

```bash
# 1. Clonar repositorio
git clone https://github.com/ryan-alej19/asistente-ciberseguridad-talleres-luis-mera.git
cd asistente-ciberseguridad-talleres-luis-mera

# 2. Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tus claves reales

# 3. Construir y correr contenedores
docker-compose up --build -d

# 4. Verificar que están corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f
```

✅ **Backend:** `http://localhost:8000`  
✅ **Frontend:** `http://localhost:3000`

### Detener contenedores
```bash
docker-compose down
```

---

## ⚙️ Variables de Entorno

Crear archivo `backend/.env` basado en `backend/.env.example`:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# APIs de Seguridad
VIRUSTOTAL_API_KEY=tu-clave-virustotal
METADEFENDER_API_KEY=tu-clave-metadefender
GOOGLE_SAFE_BROWSING_KEY=tu-clave-safe-browsing
GOOGLE_API_KEY=tu-clave-gemini
```

> ⚠️ **NUNCA** subas el archivo `.env` a GitHub. Ya está en `.gitignore`.

---

## 👥 Usuarios de Prueba

| Usuario | Contraseña | Rol | Acceso |
|---------|-----------|-----|--------|
| `admin` | `admin123` | Administrador | Panel completo + gestión usuarios |
| `analista` | `analista123` | Analista | Dashboard + gestión incidentes |
| `empleado` | `empleado123` | Empleado | Análisis + reporte propio |

---

## 🔌 APIs Integradas

### VirusTotal API v2
Analiza archivos y URLs contra más de 70 motores antivirus.
- **Límite gratuito:** 500 consultas/día
- **Documentación:** [virustotal.com/api](https://developers.virustotal.com)

### MetaDefender Cloud v4
Análisis multi-motor con más de 30 motores adicionales.
- **Límite gratuito:** Disponible en capa gratuita
- **Documentación:** [metadefender.opswat.com](https://metadefender.opswat.com)

### Google Safe Browsing v4
Verifica URLs contra listas negras oficiales de Google.
- **Límite gratuito:** Sin límite publicado para uso normal
- **Documentación:** [developers.google.com/safe-browsing](https://developers.google.com/safe-browsing)

### Google Gemini 2.5 Flash
Genera explicaciones en lenguaje natural de las amenazas detectadas.
- **Límite gratuito:** 60 consultas/minuto
- **Documentación:** [ai.google.dev](https://ai.google.dev)

---

## 📊 Métricas del Sistema

| Métrica | Objetivo | Resultado |
|---------|----------|-----------|
| Tiempo de respuesta (sin caché) | < 20 segundos | **8-12 segundos** ✅ |
| Tiempo de respuesta (con caché) | < 2 segundos | **< 500ms** ✅ |
| Reducción de consultas con caché | > 50% | **65%** ✅ |
| F1-Score clasificador heurístico | > 85% | **90.8%** ✅ |
| Detección EICAR (estándar) | > 90% | **97.1% (66/68)** ✅ |
| Usuarios simultáneos soportados | Min. 5 | **15 usuarios** ✅ |
| Costo operativo mensual | $0 | **$0** ✅ |
| Ahorro vs. proceso manual | > 90% | **98.9%** ✅ |

---

## 📸 Capturas de Pantalla

### Panel de Empleado — Análisis Multi-Motor
> Resultado de análisis mostrando detecciones de VirusTotal, MetaDefender, Google Safe Browsing y explicación de Gemini AI

### Panel de Analista — Dashboard General
> Estadísticas en tiempo real con gráficos de distribución por tipo, riesgo y estado de gestión

### Panel de Analista — Gestión de Incidentes
> Tabla completa con filtros avanzados, badges de riesgo y gestión de estados

### Panel de Administrador — Gestión de Usuarios
> Control de acceso con activación/desactivación de cuentas y cambio de roles

---

## 📚 Contexto Académico

| Campo | Detalle |
|-------|---------|
| **Título del proyecto** | Asistente Web con IA para la Gestión de Incidentes de Ciberseguridad en Talleres Luis Mera |
| **Carrera** | Tecnología Superior en Desarrollo de Software |
| **Institución** | PUCE TEC — Pontificia Universidad Católica del Ecuador, Sede Ibarra |
| **Metodología** | eXtreme Programming (XP) |
| **Cliente real** | Talleres Luis Mera — Ibarra, Ecuador |
| **Año** | 2026 |

### Alineación con Estándares
- 📋 **NIST Cybersecurity Framework** — Identificación y respuesta a incidentes
- 📋 **ISO/IEC 27035** — Gestión de incidentes de seguridad de la información
- 📋 **OWASP** — Prácticas de seguridad en desarrollo web

---

## 👨💻 Autor

<div align="center">

**Ryan Alejandro** — Estudiante TSU Desarrollo de Software  
**PUCE TEC — Ibarra, Ecuador — 2026**

[![GitHub](https://img.shields.io/badge/GitHub-ryan--alej19-181717?style=for-the-badge&logo=github)](https://github.com/ryan-alej19)

</div>

---

<div align="center">

**Desarrollado con ❤️ para Talleres Luis Mera — Ibarra, Ecuador**

*Sistema de apoyo a la toma de decisiones en ciberseguridad para PYMES ecuatorianas*

<img src="https://img.shields.io/badge/Hecho_en-Ecuador_🇪🇨-FFD100?style=for-the-badge" />

</div>
