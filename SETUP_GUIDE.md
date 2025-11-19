# Guía de Configuración - Sistema de Actividades Talkabout

## 📋 Requisitos Previos

- Docker y Docker Compose
- Git
- Acceso a servidor SMTP (para envío de emails)
- (Opcional) Cuenta de Google Cloud para Google Meet

## 🚀 Instalación y Configuración

### 1. Clonar y Configurar Entorno

```bash
# Clonar repositorio
git clone <repository-url>
cd Talkabout-Claude

# Copiar archivo de ejemplo de variables de entorno
cp .env.example .env

# Editar .env con tus configuraciones
nano .env
```

### 2. Variables de Entorno Necesarias

Edita `.env` con las siguientes configuraciones:

```bash
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=talkabout
DB_USER=talkabout_user
DB_PASSWORD=talkabout_password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Frontend
FRONTEND_URL=http://localhost:3000

# Email Configuration (ejemplo con Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
DEFAULT_FROM_EMAIL=noreply@talkabout.com

# Jitsi Configuration
JITSI_DOMAIN=meet.jit.si
JITSI_APP_ID=
JITSI_APP_SECRET=

# Google Meet (Opcional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
```

#### Configuración de Email con Gmail

1. Habilitar "Verificación en 2 pasos" en tu cuenta de Google
2. Crear una "Contraseña de aplicación":
   - Ve a https://myaccount.google.com/security
   - En "Verificación en 2 pasos", selecciona "Contraseñas de aplicaciones"
   - Genera una nueva contraseña para "Correo"
   - Usa esta contraseña en `EMAIL_HOST_PASSWORD`

### 3. Instalar Dependencias

```bash
# Agregar pytz a requirements.txt si no está
echo "pytz>=2023.3" >> backend/requirements.txt
```

### 4. Construir y Levantar Servicios

```bash
# Construir imágenes de Docker
make build

# Iniciar servicios
make up

# Ver logs (en otra terminal)
make logs
```

### 5. Ejecutar Migraciones

```bash
# Generar migraciones de los nuevos modelos
make makemigrations

# Aplicar migraciones
make migrate
```

### 6. Crear Superusuario

```bash
make createsuperuser

# Seguir las instrucciones para crear un administrador
```

### 7. Configurar Tareas Periódicas de Celery

1. Accede al panel de administración: `http://localhost:8000/admin/`
2. Ve a "Periodic Tasks" (django_celery_beat)
3. Crea las siguientes tareas:

#### Tarea 1: Primer Recordatorio (Cada hora)
```
Name: Check and send first reminders
Task: apps.events.tasks.check_and_send_first_reminders
Interval: every 1 hour
Enabled: ✓
```

#### Tarea 2: Segundo Recordatorio (Cada minuto)
```
Name: Check and send second reminders
Task: apps.events.tasks.check_and_send_second_reminders
Interval: every 1 minute
Enabled: ✓
```

#### Tarea 3: Procesar Salas de Espera (Cada minuto)
```
Name: Check and process waiting rooms
Task: apps.meetings.tasks.check_and_process_waiting_rooms
Interval: every 1 minute
Enabled: ✓
```

#### Tarea 4: Completar Reuniones Finalizadas (Cada 5 minutos)
```
Name: Complete finished meetings
Task: apps.meetings.tasks.complete_finished_meetings
Interval: every 5 minutes
Enabled: ✓
```

#### Tarea 5: Limpieza de Salas Antiguas (Diaria)
```
Name: Cleanup old waiting rooms
Task: apps.meetings.tasks.cleanup_old_waiting_rooms
Crontab: 0 2 * * * (2:00 AM diario)
Enabled: ✓
```

## 📊 Uso del Sistema

### Para Administradores

#### 1. Crear una Actividad

1. Accede al admin: `http://localhost:8000/admin/`
2. Ve a "Activities" → "Add Activity"
3. Completa:
   - **Título**: Nombre de la actividad
   - **Descripción**: Texto plano
   - **Descripción HTML**: HTML para mostrar en interfaz
   - **Max participantes por reunión**: ej. 10
   - **Min participantes por reunión**: ej. 2
   - **Tiempo de espera (minutos)**: ej. 3
   - **Primer recordatorio (horas antes)**: ej. 24
   - **Segundo recordatorio (minutos antes)**: ej. 5
4. Guarda

5. Agrega archivos si es necesario:
   - En la misma página, sección "Activity Files"
   - Sube PDFs, documentos, etc.

#### 2. Crear Eventos (Convocatorias)

1. Ve a "Events" → "Add Event"
2. Selecciona la **Actividad**
3. Configura:
   - **Start time**: Fecha y hora de inicio (UTC)
   - **End time**: Fecha y hora de fin (UTC)
4. Guarda

**Nota**: Actualmente se crean eventos uno por uno. La función de creación en bulk está pendiente de implementar en la interfaz admin.

#### 3. Ver Estadísticas

1. Ve a "Events" en el admin
2. Verás columnas con:
   - Número de inscritos (enrolled_count)
   - Número de asistentes (attended_count)

Para exportar a CSV:
- Actualmente manual desde el admin
- La función de export automático está pendiente

### Para Estudiantes

#### Inscribirse desde edX (Embebido)

```html
<!-- Código HTML para embeber en edX -->
<iframe
  src="http://tu-dominio/student/activity/ACTIVITY_CODE/?user=%%USER_ID%%"
  width="100%"
  height="600px"
  frameborder="0">
</iframe>
```

#### Inscribirse Standalone

1. Accede a: `http://tu-dominio/student/activity/ACTIVITY_CODE/`
2. Introduce tu email
3. Selecciona convocatorias
4. Confirma inscripción
5. Recibirás email de confirmación con archivo .ics

#### Flujo de Participación

1. **24h antes** (configurable): Recibes primer recordatorio
2. **5 min antes** (configurable): Recibes email con enlace a sala de espera
3. **Sala de espera**: Accedes y ves countdown
4. **Al tiempo configurado**: Sistema te redirige automáticamente a tu videoconferencia
5. El sistema agrupa automáticamente a los participantes que se conectaron

### Gestión de Respuestas en Emails

Los emails incluyen enlaces para:

- **Aceptar**: Confirma asistencia
- **Tentativo**: Marca como "quizás asista"
- **Declinar**: Cancela inscripción
- **Darse de baja**: Anonimiza cuenta y elimina datos personales

El sistema trackea todas las respuestas en `EmailNotification`.

## 🔧 Comandos Útiles

```bash
# Ver estado de servicios
docker-compose ps

# Logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f celery-beat

# Reiniciar un servicio
docker-compose restart backend

# Acceder a shell de Django
make shell

# Ejecutar comando personalizado
docker-compose exec backend python manage.py <comando>

# Detener todo
make down

# Limpiar todo (incluye volúmenes)
make clean
```

## 🧪 Pruebas

### Probar Envío de Emails

```bash
# Desde Django shell
make shell

# En el shell:
from apps.enrollments.models import Enrollment
from apps.events.tasks import send_enrollment_confirmation

# Obtener una inscripción de prueba
enrollment = Enrollment.objects.first()

# Enviar confirmación
send_enrollment_confirmation.delay(enrollment.id)

# Verificar en logs de Celery
```

### Probar Distribución de Usuarios

```bash
make shell

from apps.meetings.services import UserDistributionService

# Ejemplo: 7 usuarios, max 4, min 2
result = UserDistributionService.calculate_group_stats(
    total_users=7,
    max_participants=4,
    min_participants=2
)

print(result)
# Debería mostrar: {'num_groups': 2, 'users_per_group': [4, 3], ...}
```

### Probar Creación de Videoconferencias

```bash
make shell

from apps.meetings.services import VideoConferenceService

result = VideoConferenceService.create_meeting(
    platform='JITSI',
    meeting_title='Prueba de Reunión'
)

print(result)
# Debería mostrar: {'success': True, 'meeting_url': '...', ...}
```

## 📱 Integración con edX

### Obtener el USER_ID anonimizado de edX

En edX, puedes usar `%%USER_ID%%` que proporciona un hash SHA-1 del ID del usuario.

### Crear Componente HTML en edX

1. En Studio, agrega un componente "HTML"
2. Edita el HTML y pega:

```html
<div class="talkabout-activity">
  <iframe
    src="http://TU_DOMINIO/api/student/activity/CODIGO_ACTIVIDAD/?edx_user=%%USER_ID%%&edx_username=%%USERNAME%%"
    width="100%"
    height="800px"
    frameborder="0"
    allow="camera; microphone">
  </iframe>
</div>
```

3. Reemplaza:
   - `TU_DOMINIO`: Tu dominio del servidor
   - `CODIGO_ACTIVIDAD`: El `activity_code` de la actividad

## 🌍 Zonas Horarias

El sistema maneja zonas horarias automáticamente:

1. **Backend**: Almacena todo en UTC
2. **Frontend**: Captura zona horaria del navegador del usuario
3. **Emails**: Muestran horas en zona horaria del usuario
4. **iCalendar**: Genera eventos en UTC pero con información de zona horaria

## 🔒 Seguridad

### Protección de Datos Personales

- Los usuarios pueden darse de baja en cualquier momento
- Al darse de baja, se ejecuta `user.anonymize()`:
  - Email → `anonymized_<uuid>@deleted.local`
  - Nombre y apellidos → vacío
  - External ID → `ANONYMIZED_<uuid>`
  - Usuario marcado como inactivo
  - **Estadísticas se preservan**

### Tokens de Seguridad

- Salas de espera: UUID único no predecible
- Links de respuesta en emails: UUID único por notificación
- Acceso a salas solo con token válido

## 🐛 Troubleshooting

### Emails no se envían

1. Verifica logs de Celery:
   ```bash
   docker-compose logs -f celery
   ```

2. Prueba configuración de email:
   ```bash
   make shell
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

3. Verifica `EmailNotification` en admin para ver errores

### Tareas de Celery no se ejecutan

1. Verifica que Celery Beat está corriendo:
   ```bash
   docker-compose ps celery-beat
   ```

2. Verifica tareas periódicas en admin:
   - `/admin/django_celery_beat/periodictask/`

3. Revisa logs:
   ```bash
   docker-compose logs -f celery-beat
   ```

### Salas de espera no se procesan

1. Verifica que `check_and_process_waiting_rooms` está configurada
2. Verifica logs:
   ```bash
   docker-compose logs -f celery | grep "waiting_room"
   ```
3. Revisa estado de WaitingRoom en admin

### Videoconferencias no se crean

1. Para Jitsi (default):
   - No requiere configuración adicional
   - Funciona con `meet.jit.si`

2. Para Google Meet:
   - Requiere configuración de Google Cloud API
   - Actualmente es placeholder, necesita implementación

## 📊 Monitoreo

### Verificar Estado del Sistema

```bash
# Ver tareas pendientes de Celery
docker-compose exec backend python manage.py shell
from django_celery_beat.models import PeriodicTask
PeriodicTask.objects.filter(enabled=True)

# Ver eventos próximos
from apps.events.models import Event
from django.utils import timezone
Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')[:10]

# Ver salas de espera activas
from apps.activities.models import WaitingRoom
WaitingRoom.objects.filter(status='WAITING')
```

## 🎯 Siguientes Pasos

1. **Completar APIs REST**: Implementar ViewSets para estudiantes
2. **Frontend**: Desarrollar componente embebible en React
3. **Panel Admin Mejorado**: Interfaz para creación bulk de eventos
4. **Tests**: Agregar tests unitarios y de integración
5. **Google Meet**: Completar integración con Google Calendar API
6. **Analytics**: Dashboard de estadísticas avanzadas

## 📞 Soporte

Para problemas o preguntas:
- Revisa logs: `make logs`
- Consulta documentación: `IMPLEMENTATION_COMPLETE.md`
- Issues: GitHub repository
