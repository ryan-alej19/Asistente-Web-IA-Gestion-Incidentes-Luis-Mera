# ASISTENTE WEB CON INTELIGENCIA ARTIFICIAL PARA LA GESTIÓN DE INCIDENTES DE CIBERSEGURIDAD EN TALLERES LUIS MERA

> Tesis de Tecnología Superior en Desarrollo de Software  
> Pontificia Universidad Católica del Ecuador - Sede Ibarra (PUCE TEC)  
> Febrero 2026

## Descripción

Sistema web para la gestión de incidentes de ciberseguridad orientado a PYMES.
Permite clasificar, priorizar y analizar reportes de incidentes mediante
inteligencia artificial explicable (Google Gemini 2.5 Flash), integrando
múltiples motores de análisis de amenazas.

## Tecnologías

- **Backend:** Django 5.x + Django REST Framework + JWT
- **Frontend:** React 18 + Tailwind CSS + Framer Motion
- **IA:** Google Gemini 2.5 Flash
- **APIs:** VirusTotal, MetaDefender Cloud, Google Safe Browsing
- **Base de datos:** SQLite (desarrollo) 
- **Despliegue:** Docker + Render.com

## Roles del sistema

| Rol | Descripción |
|-----|-------------|
| Empleado | Analiza archivos/URLs y reporta incidentes |
| Analista | Gestiona y revisa todos los incidentes |
| Administrador | Control total + gestión de usuarios |

## Instalación local

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env   # Configurar variables
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## Usuarios de demo

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| analista | analista123 | Analista |
| empleado | empleado123 | Empleado |

## Créditos

Desarrollado por: Ryan Alejandro  
Cliente: Talleres Luis Mera - Ibarra, Ecuador  
Tutor: [Nombre del tutor]
