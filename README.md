# Talkabout - Plataforma de Actividades de Conversación para MOOCs

Talkabout es una aplicación web diseñada para facilitar actividades de conversación en cursos MOOC (Massive Open Online Courses). Permite a profesores crear actividades con múltiples convocatorias temporales, gestionar inscripciones de estudiantes, y lanzar automáticamente videoconferencias usando Google Meet o Jitsi.

## Características Principales

- **Gestión de Actividades**: Profesores pueden crear actividades de conversación con descripciones y archivos adjuntos
- **Eventos Programados**: Múltiples convocatorias temporales para cada actividad en diferentes días y horarios
- **Inscripción de Estudiantes**: Los estudiantes pueden inscribirse en los eventos que prefieran
- **Notificaciones Automáticas**: Envío de correos electrónicos recordatorios antes de cada evento
- **División Inteligente de Grupos**: Distribución automática de participantes en grupos según límites configurables
- **Integración con Videoconferencias**: Soporte para Google Meet y Jitsi
- **Estadísticas Completas**: Seguimiento de inscripciones, asistencias y tasas de participación
- **Integración con edX**: Soporte para usuarios provenientes de edX mediante USER_ID

## Arquitectura

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Base de Datos**: PostgreSQL 15
- **Tareas Asíncronas**: Celery + Redis
- **Autenticación**: JWT (JSON Web Tokens)
- **Documentación API**: OpenAPI (Swagger)

### Estructura de Apps
```
backend/
├── apps/
│   ├── users/          # Gestión de usuarios y autenticación
│   ├── activities/     # Actividades de conversación
│   ├── events/         # Eventos programados
│   ├── enrollments/    # Inscripciones de usuarios
│   ├── meetings/       # Reuniones y videoconferencias
│   └── statistics/     # Estadísticas y reportes
```

### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI 5
- **Routing**: React Router 6
- **HTTP Client**: Axios
- **State Management**: Context API
- **Date Handling**: date-fns

### Estructura Frontend
```
frontend/
├── src/
│   ├── components/      # Componentes reutilizables
│   ├── contexts/        # Context API (Auth)
│   ├── pages/           # Páginas de la aplicación
│   ├── services/        # API services
│   └── App.js           # Componente principal
```

## Modelo de Datos

### Entidades Principales

#### User (Usuario)
- **Roles**: ADMIN, TEACHER, STUDENT
- **Campos**: username, email, role, external_id (para edX), user_code
- **Autenticación**: JWT con refresh tokens

#### Activity (Actividad)
- Creada por profesores
- Contiene: título, descripción, archivos adjuntos
- Configuración: max/min participantes por reunión

#### Event (Evento)
- Convocatoria temporal para una actividad
- Estados: SCHEDULED, NOTIFIED, IN_PROGRESS, COMPLETED, CANCELLED
- Horario: start_time, end_time

#### Enrollment (Inscripción)
- Relación usuario-evento
- Estado: activa o cancelada

#### Meeting (Reunión)
- Videoconferencia creada automáticamente
- Plataformas: JITSI o GOOGLE_MEET
- Estados: SCHEDULED, STARTED, COMPLETED, FAILED

#### Attendance (Asistencia)
- Registro de participación en reunión
- Métricas: joined_at, left_at, duration

## Instalación y Configuración

### Requisitos Previos
- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)
- Node.js 18+ (para el frontend)

### Configuración Rápida con Docker

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd Talkabout-Claude
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Iniciar servicios con Docker Compose**
```bash
docker-compose up -d
```

4. **Ejecutar migraciones**
```bash
docker-compose exec backend python manage.py migrate
```

5. **Crear superusuario**
```bash
docker-compose exec backend python manage.py createsuperuser
```

6. **Acceder a la aplicación**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Django Admin: http://localhost:8000/admin
- API Documentation: http://localhost:8000/api/docs

### Desarrollo Local (sin Docker)

#### Backend

1. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar PostgreSQL**
Crear base de datos `talkabout` y usuario

4. **Ejecutar migraciones**
```bash
cd backend
python manage.py migrate
```

5. **Crear superusuario**
```bash
python manage.py createsuperuser
```

6. **Iniciar servidor**
```bash
python manage.py runserver
```

#### Celery (para tareas asíncronas)

En terminales separadas:

```bash
# Worker
celery -A talkabout worker -l info

# Beat scheduler
celery -A talkabout beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## API Endpoints

### Autenticación
```
POST   /api/auth/token/                  # Obtener token JWT
POST   /api/auth/token/refresh/          # Refrescar token
POST   /api/auth/users/                  # Registrar usuario
GET    /api/auth/users/me/               # Perfil actual
POST   /api/auth/users/logout/           # Cerrar sesión
```

### Actividades
```
GET    /api/activities/                  # Listar actividades
POST   /api/activities/                  # Crear actividad (teacher)
GET    /api/activities/{id}/             # Detalle de actividad
PUT    /api/activities/{id}/             # Actualizar actividad
DELETE /api/activities/{id}/             # Eliminar actividad
POST   /api/activities/{id}/upload_file/ # Subir archivo
GET    /api/activities/{id}/files/       # Listar archivos
```

### Eventos
```
GET    /api/events/                      # Listar eventos
POST   /api/events/                      # Crear evento (teacher)
GET    /api/events/{id}/                 # Detalle de evento
GET    /api/events/{id}/enrollments/     # Inscripciones del evento
```

### Inscripciones
```
GET    /api/enrollments/                 # Listar inscripciones
POST   /api/enrollments/                 # Inscribirse a evento
GET    /api/enrollments/my_enrollments/  # Mis inscripciones
POST   /api/enrollments/{id}/cancel/     # Cancelar inscripción
```

### Reuniones
```
GET    /api/meetings/                    # Listar reuniones
GET    /api/meetings/{id}/               # Detalle de reunión
POST   /api/meetings/{id}/join/          # Unirse a reunión
POST   /api/meetings/{id}/leave/         # Salir de reunión
```

### Estadísticas
```
GET    /api/statistics/activities/       # Estadísticas de actividades
GET    /api/statistics/events/           # Estadísticas de eventos
GET    /api/statistics/users/            # Estadísticas de usuarios (admin)
GET    /api/statistics/my_stats/         # Mis estadísticas
```

## Flujo de Trabajo

### Para Profesores

1. **Crear Actividad**
   - Definir título y descripción
   - Configurar límites de participantes
   - Adjuntar archivos si es necesario

2. **Programar Eventos**
   - Crear múltiples eventos para la actividad
   - Establecer fechas y horarios
   - Los estudiantes podrán inscribirse

3. **Monitorear Inscripciones**
   - Ver quién se ha inscrito
   - Recibir estadísticas en tiempo real

4. **Revisar Resultados**
   - Ver asistencias reales
   - Analizar tasas de participación

### Para Estudiantes

1. **Registrarse** (o ingresar desde edX)
2. **Explorar Actividades** disponibles
3. **Inscribirse a Eventos** que le interesen
4. **Recibir Notificaciones** por email
5. **Unirse a Videoconferencia** cuando llegue el momento
6. **Ver Estadísticas** personales

### Sistema Automático

1. **Scheduler de Celery** revisa constantemente eventos próximos
2. **24 horas antes**: Envía email recordatorio a inscritos
3. **Al inicio del evento**:
   - Divide participantes en grupos
   - Crea reuniones (Jitsi o Google Meet)
   - Envía enlaces de videoconferencia
4. **Durante la reunión**: Registra asistencias
5. **Al finalizar**: Marca reunión como completada

## Configuración de Integraciones

### Jitsi Meet

Por defecto, usa el servidor público `meet.jit.si`. Para usar tu propio servidor:

```env
JITSI_DOMAIN=tu-servidor.jitsi.com
JITSI_APP_ID=tu_app_id
JITSI_APP_SECRET=tu_app_secret
```

### Google Meet

Requiere credenciales de Google Cloud Platform:

1. Crear proyecto en Google Cloud
2. Habilitar Google Calendar API
3. Crear credenciales de cuenta de servicio
4. Descargar `credentials.json` al directorio del backend
5. Configurar variables:

```env
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret
```

### Email

Configurar SMTP en `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

## Tareas Celery Programadas

### `check_upcoming_events`
- **Frecuencia**: Cada 5 minutos
- **Función**: Detecta eventos próximos y programa notificaciones

### `start_scheduled_meetings`
- **Frecuencia**: Cada minuto
- **Función**: Crea reuniones para eventos que están por comenzar

### `complete_finished_meetings`
- **Frecuencia**: Cada 5 minutos
- **Función**: Marca reuniones finalizadas

## Seguridad

- **Autenticación JWT** con tokens de acceso y refresh
- **Permisos basados en roles** (Admin, Teacher, Student)
- **Validación de datos** en todos los endpoints
- **CORS configurado** para frontend específico
- **Passwords hasheados** con Django's PBKDF2
- **Rate limiting** (recomendado en producción)

## Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=apps
```

## Deployment

### Producción con Docker

1. Actualizar `docker-compose.prod.yml`
2. Configurar variables de entorno de producción
3. Usar servidor WSGI (Gunicorn)
4. Configurar HTTPS con Nginx/Traefik
5. Usar base de datos PostgreSQL gestionada
6. Configurar backups automáticos

### Variables de Entorno Importantes

```env
DEBUG=False
SECRET_KEY=<generar-clave-segura>
ALLOWED_HOSTS=tu-dominio.com
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

## Contribuir

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

[Especificar licencia]

## Soporte

Para preguntas o problemas, abrir un issue en GitHub.

## Roadmap

- [ ] Frontend React completo
- [ ] App móvil (React Native)
- [ ] Integración con más plataformas LMS
- [ ] Análisis de sentimiento en conversaciones
- [ ] Grabación de reuniones
- [ ] Chat integrado
- [ ] Gamificación y badges

## Créditos

Desarrollado para facilitar el aprendizaje colaborativo en MOOCs.
