# Talkabout Backend

Backend de la aplicación Talkabout construido con Django y Django REST Framework.

## Estructura del Proyecto

```
backend/
├── talkabout/              # Configuración principal del proyecto
│   ├── settings.py         # Configuración de Django
│   ├── urls.py             # URLs principales
│   ├── celery.py           # Configuración de Celery
│   └── wsgi.py             # WSGI application
├── apps/                   # Aplicaciones Django
│   ├── users/              # Usuarios y autenticación
│   ├── activities/         # Actividades de conversación
│   ├── events/             # Eventos programados
│   ├── enrollments/        # Inscripciones
│   ├── meetings/           # Reuniones y videoconferencias
│   └── statistics/         # Estadísticas
├── media/                  # Archivos subidos por usuarios
└── manage.py               # Django management script
```

## Comandos Útiles

### Migraciones
```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver SQL de migración
python manage.py sqlmigrate <app> <migration_number>
```

### Datos de Prueba
```bash
# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Shell con IPython
python manage.py shell -i ipython
```

### Servidor de Desarrollo
```bash
# Iniciar servidor
python manage.py runserver

# En puerto específico
python manage.py runserver 8080
```

### Celery
```bash
# Worker
celery -A talkabout worker -l info

# Beat scheduler
celery -A talkabout beat -l info

# Worker + Beat
celery -A talkabout worker -l info -B
```

### Archivos Estáticos
```bash
# Recolectar archivos estáticos
python manage.py collectstatic
```

## Apps

### Users
- Modelo de usuario personalizado con roles
- Autenticación JWT
- Endpoints de registro, login, perfil

### Activities
- CRUD de actividades
- Subida de archivos
- Permisos por propietario

### Events
- Eventos programados para actividades
- Estados del evento
- Sistema de notificaciones

### Enrollments
- Inscripción de usuarios a eventos
- Cancelación de inscripciones
- Validaciones de capacidad

### Meetings
- Creación automática de reuniones
- Integración con Jitsi y Google Meet
- División de participantes en grupos
- Registro de asistencias

### Statistics
- Estadísticas por actividad
- Estadísticas por evento
- Estadísticas por usuario
- Tasas de asistencia

## Modelos Principales

```python
# User
- username, email, password
- role (ADMIN, TEACHER, STUDENT)
- external_id (para edX)
- user_code (UUID único)

# Activity
- title, description
- created_by (Teacher)
- max_participants_per_meeting
- files (through ActivityFile)

# Event
- activity (FK)
- start_time, end_time
- status (SCHEDULED, NOTIFIED, IN_PROGRESS, COMPLETED)

# Enrollment
- user, event
- is_active
- enrolled_at, cancelled_at

# Meeting
- event (FK)
- platform (JITSI, GOOGLE_MEET)
- meeting_url, meeting_id
- status, max_participants

# Attendance
- user, meeting
- joined_at, left_at, duration
```

## API Documentation

La documentación interactiva de la API está disponible en:
- Swagger UI: http://localhost:8000/api/docs/
- Schema: http://localhost:8000/api/schema/

## Testing

```bash
# Ejecutar todos los tests
pytest

# Tests de una app específica
pytest apps/users/tests/

# Con cobertura
pytest --cov=apps --cov-report=html
```

## Configuración de Desarrollo

1. Copiar `.env.example` a `.env`
2. Ajustar configuraciones según necesidad
3. Ejecutar migraciones
4. Crear superusuario
5. Iniciar servidor y Celery

## Notas de Seguridad

- Nunca commitear `.env` con datos sensibles
- Usar SECRET_KEY única en producción
- Configurar ALLOWED_HOSTS apropiadamente
- Habilitar HTTPS en producción
- Usar PostgreSQL en producción (no SQLite)
