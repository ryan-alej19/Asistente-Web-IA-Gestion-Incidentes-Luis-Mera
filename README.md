<div align="center">

<img src="https://www.pucesi.edu.ec/web/wp-content/uploads/2019/04/logo-PUCE-SI.png" alt="PUCE TEC" width="200"/>

<br/><br/>

# Asistente Web con Inteligencia Artificial para la Gestión de Incidentes de Ciberseguridad en Talleres Luis Mera

**Trabajo de Integración Curricular**  
Tecnología Superior en Desarrollo de Software  
Pontificia Universidad Católica del Ecuador — Sede Ibarra

<br/>

![Django](https://img.shields.io/badge/Django-5.1.4-092E20?style=flat-square&logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Disponible-2496ED?style=flat-square&logo=docker&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)

</div>

---

## Sobre el proyecto

Este sistema fue desarrollado como proyecto de tesis para **Talleres Luis Mera**, un taller automotriz ubicado en Ibarra, Ecuador. La idea surgió de una necesidad real: el personal del taller no tenía manera fácil de identificar si un archivo o enlace recibido por correo era peligroso, y tampoco existía un registro de estos incidentes.

La solución es una aplicación web que permite analizar archivos y URLs sospechosas de forma automática, usando cuatro servicios de seguridad externos y una IA (Google Gemini) que explica los resultados en un lenguaje que cualquier persona puede entender, sin necesidad de ser técnico.

> **Importante:** Este sistema no es un antivirus ni un monitor de red. Es una herramienta de apoyo para que las personas puedan tomar mejores decisiones frente a posibles amenazas digitales.

---

## ¿Qué puede hacer el sistema?

El sistema tiene tres tipos de usuarios, cada uno con acceso a funciones distintas:

**Empleado** — El trabajador del taller puede analizar cualquier archivo o URL sospechosa y ver el resultado con un indicador de color (rojo, amarillo, azul, verde). Si algo parece peligroso, puede crear un reporte de incidente con un clic.

**Analista** — El dueño del taller tiene acceso a todos los incidentes reportados, puede ver los detalles técnicos completos, cambiar el estado de cada caso (pendiente → en revisión → resuelto) y dejar notas internas. También tiene un panel con estadísticas generales.

**Administrador** — Además de todo lo anterior, puede gestionar los usuarios del sistema: activar o desactivar cuentas y cambiar roles.

---

## Tecnologías utilizadas

**Backend:** Django 5.1.4 con Django REST Framework, base de datos SQLite, autenticación JWT.

**Frontend:** React 18, Tailwind CSS, TailwindUI, Lucide React para iconos, Framer Motion para animaciones, Recharts para gráficas.

**APIs de seguridad:** VirusTotal API v2, MetaDefender Cloud v4, Google Safe Browsing v4, Google Gemini 2.5 Flash.

**Despliegue:** Docker para contenedorización, Render.com para el servidor en la nube.

Todo el sistema opera en las capas gratuitas de todas las APIs, sin costo mensual.

---

## Estructura del proyecto

```
Asistente-Web-IA-Gestion-Incidentes-Luis-Mera/
├── backend/                    # Servidor Django
│   ├── config/                 # Configuración del proyecto
│   ├── users/                  # Manejo de usuarios y roles
│   ├── incidents/              # Módulo de incidentes
│   ├── analysis/               # Motor de análisis multi-API
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # Aplicación React
│   ├── src/
│   │   ├── pages/              # Páginas principales
│   │   ├── components/         # Componentes reutilizables
│   │   └── config/             # Configuración de API
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Instalación y ejecución

### Requisitos previos

- Python 3.11 o superior
- Node.js 18 o superior
- Las claves de API correspondientes (VirusTotal, MetaDefender, Google)

### Opción 1 — Sin Docker (desarrollo local)

**Backend:**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux o Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Editar .env con las claves reales

python manage.py migrate
python manage.py runserver
```

**Frontend** (en otra terminal):
```bash
cd frontend
npm install
npm start
```

El backend queda en `http://localhost:8000` y el frontend en `http://localhost:3000`.

### Opción 2 — Con Docker

```bash
# Configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con las claves reales

# Construir y levantar los contenedores
docker-compose up --build -d

# Ver que estén corriendo
docker-compose ps
```

Para detenerlos:
```bash
docker-compose down
```

---

## Variables de entorno

Copiar `backend/.env.example` como `backend/.env` y completar los valores:

```env
SECRET_KEY=clave-secreta-django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

VIRUSTOTAL_API_KEY=tu-clave
METADEFENDER_API_KEY=tu-clave
GOOGLE_SAFE_BROWSING_KEY=tu-clave
GOOGLE_API_KEY=tu-clave-gemini
```

> El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

---

## Usuarios de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| analista | analista123 | Analista |
| empleado | empleado123 | Empleado |

---

## Resultados del sistema

Durante las pruebas del sistema se obtuvieron los siguientes resultados:

| Métrica | Resultado |
|---------|-----------|
| Tiempo de análisis completo | 8 a 12 segundos |
| Tiempo con caché activo | Menos de 500ms |
| Reducción de consultas con caché | 65% |
| F1-Score del clasificador heurístico | 90.8% |
| Detección del archivo estándar EICAR | 97.1% (66 de 68 motores) |
| Ahorro de tiempo vs. proceso manual | 98.9% |
| Costo mensual de operación | $0 |

---

## Contexto académico

| | |
|--|--|
| **Carrera** | Tecnología Superior en Desarrollo de Software |
| **Institución** | PUCE TEC — Pontificia Universidad Católica del Ecuador, Sede Ibarra |
| **Metodología de desarrollo** | eXtreme Programming (XP) |
| **Cliente** | Talleres Luis Mera, Ibarra |
| **Año** | 2026 |

---

## Autor

Desarrollado por **Ryan Alejandro** como Trabajo de Integración Curricular para obtener el título de Tecnólogo Superior en Desarrollo de Software en la PUCE TEC, Ibarra — Ecuador, 2026.

---

<div align="center">
<sub>Pontificia Universidad Católica del Ecuador — Sede Ibarra · 2026</sub>
</div>
