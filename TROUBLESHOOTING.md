# Guía de Solución de Problemas - Talkabout

## Problemas Comunes y Soluciones

### 1. Error: "requirements.txt not found" al construir Docker

**Problema:** Docker no encuentra el archivo `requirements.txt` al construir el backend.

**Solución:**
```bash
# El archivo requirements.txt debe estar en backend/
ls backend/requirements.txt

# Si no está ahí, el proyecto está corrupto. Clona de nuevo o verifica que:
# - backend/requirements.txt existe
# - backend/Dockerfile tiene: COPY requirements.txt /app/
```

### 2. Error: "port already allocated" al iniciar servicios

**Problema:** Los puertos 3000, 8000, 5432 o 6379 ya están en uso.

**Solución:**
```bash
# Opción 1: Detener otros servicios
docker-compose down
docker ps  # Ver qué más está corriendo

# Opción 2: Cambiar puertos en docker-compose.yml
# Ejemplo: cambiar 8000:8000 por 8001:8000
```

### 3. Error de conexión a la base de datos

**Problema:** El backend no puede conectarse a PostgreSQL.

**Solución:**
```bash
# 1. Verificar que la BD está corriendo
docker-compose ps

# 2. Ver logs de PostgreSQL
docker-compose logs db

# 3. Reiniciar servicios en orden
docker-compose down
docker-compose up -d db
sleep 10
docker-compose up -d backend celery celery-beat frontend

# 4. Ejecutar migraciones
docker-compose exec backend python manage.py migrate
```

### 4. Frontend no se conecta al Backend

**Problema:** Errores CORS o "Network Error" en el frontend.

**Solución:**
```bash
# 1. Verificar que backend está corriendo
curl http://localhost:8000/api/

# 2. Verificar configuración CORS en backend/talkabout/settings.py
# Debe incluir: CORS_ALLOWED_ORIGINS = ['http://localhost:3000']

# 3. Verificar proxy en frontend/package.json
# Debe tener: "proxy": "http://backend:8000"

# 4. Reiniciar frontend
docker-compose restart frontend
```

### 5. Celery no procesa tareas

**Problema:** No se envían emails o no se crean reuniones automáticamente.

**Solución:**
```bash
# 1. Ver logs de Celery
docker-compose logs celery
docker-compose logs celery-beat

# 2. Verificar conexión a Redis
docker-compose exec redis redis-cli ping
# Debe responder: PONG

# 3. Reiniciar workers
docker-compose restart celery celery-beat
```

### 6. Error "No module named 'apps'"

**Problema:** Python no encuentra los módulos de las apps.

**Solución:**
```bash
# Verificar que manage.py está en el directorio correcto
docker-compose exec backend ls -la /app/
# Debe mostrar: manage.py, apps/, talkabout/

# Reconstruir el contenedor
docker-compose down
docker-compose build backend
docker-compose up -d
```

### 7. Migraciones fallan

**Problema:** `python manage.py migrate` da errores.

**Solución:**
```bash
# 1. Ver logs detallados
docker-compose exec backend python manage.py migrate --verbosity 3

# 2. Resetear base de datos (¡CUIDADO: borra todo!)
docker-compose down -v  # Elimina volúmenes
docker-compose up -d db
sleep 10
docker-compose exec backend python manage.py migrate

# 3. Si hay conflictos de migraciones
docker-compose exec backend python manage.py showmigrations
docker-compose exec backend python manage.py migrate --fake-initial
```

### 8. Frontend muestra página en blanco

**Problema:** React no carga correctamente.

**Solución:**
```bash
# 1. Ver logs del frontend
docker-compose logs frontend

# 2. Verificar que node_modules se instaló
docker-compose exec frontend ls node_modules/
# Debe mostrar muchas carpetas

# 3. Reconstruir frontend
docker-compose down
docker-compose build frontend
docker-compose up -d frontend

# 4. Acceder a los logs en tiempo real
docker-compose logs -f frontend
```

### 9. No se cargan los datos de prueba

**Problema:** El script init_db.py falla.

**Solución:**
```bash
# 1. Verificar que las migraciones están aplicadas
docker-compose exec backend python manage.py migrate

# 2. Ejecutar el script con más detalle
docker-compose exec backend python manage.py shell
>>> exec(open('/app/../scripts/init_db.py').read())

# 3. Crear datos manualmente
docker-compose exec backend python manage.py createsuperuser
```

### 10. Cambios en el código no se reflejan

**Problema:** Editas archivos pero no ves los cambios.

**Solución:**
```bash
# Backend: Django tiene auto-reload, pero a veces hay que reiniciar
docker-compose restart backend

# Frontend: Debe tener hot-reload, si no funciona:
docker-compose restart frontend

# Si cambiaste modelos o settings:
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
docker-compose restart backend celery celery-beat
```

### 11. Error al subir archivos

**Problema:** Falla al subir archivos a actividades.

**Solución:**
```bash
# Verificar que el directorio media existe y tiene permisos
docker-compose exec backend ls -la /app/media/

# Crear si no existe
docker-compose exec backend mkdir -p /app/media/activities
docker-compose exec backend chmod -R 755 /app/media/
```

### 12. Google Meet no funciona

**Problema:** No se crean reuniones de Google Meet.

**Solución:**
```bash
# Google Meet requiere credenciales reales
# 1. Obtén credentials.json de Google Cloud Console
# 2. Cópialo a backend/
docker-compose cp credentials.json backend:/app/

# 3. Actualiza .env con tus credenciales
# GOOGLE_CLIENT_ID=...
# GOOGLE_CLIENT_SECRET=...

# Mientras tanto, usa Jitsi (funciona sin configuración)
```

## Comandos Útiles de Diagnóstico

```bash
# Ver todos los contenedores
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs

# Ver logs de un servicio específico
docker-compose logs backend
docker-compose logs -f frontend  # Seguir logs en tiempo real

# Ejecutar comandos dentro de contenedores
docker-compose exec backend python manage.py shell
docker-compose exec backend bash
docker-compose exec frontend sh

# Reconstruir todo desde cero
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# Ver uso de recursos
docker stats

# Limpiar Docker (libera espacio)
docker system prune -a
```

## Verificación de Salud del Sistema

```bash
# Script de verificación rápida
echo "=== Verificación de Servicios ==="
echo ""
echo "Backend API:"
curl -s http://localhost:8000/api/ && echo "✓ OK" || echo "✗ FAIL"
echo ""
echo "Frontend:"
curl -s http://localhost:3000 && echo "✓ OK" || echo "✗ FAIL"
echo ""
echo "PostgreSQL:"
docker-compose exec db pg_isready && echo "✓ OK" || echo "✗ FAIL"
echo ""
echo "Redis:"
docker-compose exec redis redis-cli ping && echo "✓ OK" || echo "✗ FAIL"
```

## Resetear Todo (Último Recurso)

```bash
# ADVERTENCIA: Esto borra TODO (base de datos, volúmenes, contenedores)
docker-compose down -v
docker system prune -a
docker volume prune

# Luego vuelve a iniciar
./start.sh
```

## ¿Necesitas Ayuda?

Si ninguna de estas soluciones funciona:

1. Revisa los logs completos:
   ```bash
   docker-compose logs > logs.txt
   ```

2. Verifica las versiones:
   ```bash
   docker --version
   docker-compose --version
   ```

3. Abre un issue en GitHub con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Tu sistema operativo
   - Versiones de Docker
