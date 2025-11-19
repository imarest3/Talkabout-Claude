# 🔍 Diagnóstico de Problemas - Talkabout

Este documento describe cómo usar el script de diagnóstico para identificar problemas en el proyecto.

## Script de Diagnóstico Automático

### `diagnose_project.sh`

Script completo que verifica todos los aspectos del proyecto y genera un reporte detallado.

#### Uso

```bash
./diagnose_project.sh
```

#### ¿Qué Verifica?

El script realiza las siguientes verificaciones:

1. **Estructura de Directorios**
   - ✓ Verifica que existan los directorios principales (backend, frontend, scripts)
   - ✓ Valida archivos críticos (manage.py, settings.py, docker-compose.yml)

2. **Variables de Entorno**
   - ✓ Comprueba existencia de archivo `.env`
   - ✓ Valida variables críticas (SECRET_KEY, DB_*, REDIS_URL)

3. **Apps de Django**
   - ✓ Verifica que todas las apps existan
   - ✓ Valida archivos necesarios (models.py, __init__.py, apps.py)

4. **Migraciones**
   - ✓ Comprueba directorios de migraciones
   - ✓ Cuenta archivos de migración por app
   - ✓ **Identifica si faltan migraciones (causa principal del error)**

5. **Docker**
   - ✓ Verifica instalación de Docker
   - ✓ Comprueba si Docker daemon está corriendo
   - ✓ Lista estado de contenedores
   - ✓ Verifica contenedores críticos (db, backend, redis)

6. **Base de Datos PostgreSQL**
   - ✓ Prueba conexión a PostgreSQL
   - ✓ Cuenta tablas en la base de datos
   - ✓ **Verifica existencia de tabla `users_user`**
   - ✓ Lista tablas existentes

7. **Configuración de Django**
   - ✓ Valida AUTH_USER_MODEL
   - ✓ Verifica INSTALLED_APPS
   - ✓ Comprueba configuración de base de datos

8. **Dependencias Python**
   - ✓ Verifica requirements.txt
   - ✓ Valida paquetes críticos (Django, DRF, psycopg2)

9. **Logs del Backend**
   - ✓ Muestra últimos 30 logs si el contenedor está corriendo

10. **Scripts de Solución**
    - ✓ Verifica existencia de scripts de solución
    - ✓ Comprueba permisos de ejecución

#### Output

El script genera:

1. **Salida en consola con colores:**
   - 🟢 Verde: Verificaciones exitosas
   - 🟡 Amarillo: Advertencias
   - 🔴 Rojo: Errores críticos
   - 🔵 Azul: Información adicional

2. **Archivo de reporte:**
   - Nombre: `diagnostic_report_YYYYMMDD_HHMMSS.log`
   - Contiene: Toda la salida del diagnóstico
   - Ubicación: Directorio raíz del proyecto

3. **Resumen final:**
   ```
   Estadísticas:
     ✓ Verificaciones exitosas: XX
     ⚠ Advertencias: XX
     ✗ Errores críticos: XX

   PROBLEMA PRINCIPAL IDENTIFICADO:
     ✗ [Descripción del problema]

   SOLUCIÓN:
     [Pasos para resolver]
   ```

#### Ejemplo de Salida

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIAGNÓSTICO COMPLETO - PROYECTO TALKABOUT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ℹ INFO: Fecha: 2025-11-19 13:51:14
ℹ INFO: Directorio: /home/user/Talkabout-Claude

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. MIGRACIONES DE DJANGO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ ERROR: Directorio migrations/ NO existe para 'users'
ℹ INFO:   Ejecutar: docker-compose exec backend python manage.py makemigrations users

...

PROBLEMA PRINCIPAL IDENTIFICADO:
  ✗ No existen directorios de migraciones

CAUSA DEL ERROR:
  django.db.utils.ProgrammingError: relation 'users_user' does not exist

SOLUCIÓN:
  1. Ejecutar: ./setup_from_scratch.sh
```

## Problemas Comunes Identificados

### Error: `relation "users_user" does not exist`

**Causa:** Las migraciones de Django no se han creado ni aplicado.

**Solución automática:**
```bash
./setup_from_scratch.sh
```

**Solución manual:**
```bash
# 1. Crear archivo .env
cp .env.example .env

# 2. Iniciar servicios
docker-compose up -d db backend

# 3. Crear migraciones
docker-compose exec backend python manage.py makemigrations

# 4. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 5. Cargar datos de prueba
docker-compose exec backend python manage.py shell < scripts/init_db.py
```

### Error: `.env` no existe

**Causa:** Variables de entorno no configuradas.

**Solución:**
```bash
cp .env.example .env
# Editar .env si es necesario
```

### Error: Docker no está corriendo

**Causa:** Docker daemon no está activo.

**Solución:**
- Linux: `sudo systemctl start docker`
- macOS/Windows: Iniciar Docker Desktop

### Error: Contenedor de BD no responde

**Causa:** PostgreSQL necesita más tiempo para inicializar.

**Solución:**
```bash
docker-compose up -d db
sleep 15
docker-compose exec db pg_isready -U talkabout_user -d talkabout
```

## Archivos Generados

Los reportes de diagnóstico se guardan en:
```
diagnostic_report_YYYYMMDD_HHMMSS.log
```

**Nota:** Estos archivos están en `.gitignore` y no se commitean.

## Interpretación de Resultados

### Códigos de Salida

- `0`: Sin errores críticos
- `1`: Se encontraron errores críticos

### Estadísticas

```
✓ Verificaciones exitosas: 46   ← Todo lo que está bien
⚠ Advertencias: 2                ← No crítico pero revisar
✗ Errores críticos: 9            ← Requieren acción inmediata
```

## Cuándo Ejecutar el Diagnóstico

Ejecuta el script de diagnóstico cuando:

1. ❌ Encuentres errores al iniciar el proyecto
2. ❌ Veas errores de base de datos
3. ❌ Los servicios Docker no inicien correctamente
4. ❌ Las migraciones fallen
5. ℹ️ Después de clonar el repositorio
6. ℹ️ Antes de reportar un bug
7. ℹ️ Cuando quieras verificar el estado del proyecto

## Scripts Relacionados

- `./diagnose_project.sh` - Diagnóstico completo (este script)
- `./setup_from_scratch.sh` - Inicialización completa desde cero
- `./fix_auth.sh` - Solución rápida para problemas de autenticación

## Soporte

Si el script de diagnóstico identifica errores que no puedes resolver:

1. Revisa el archivo de reporte generado
2. Consulta la documentación específica:
   - `TROUBLESHOOTING.md` - Problemas generales
   - `AUTHENTICATION_TROUBLESHOOTING.md` - Problemas de auth
   - `DATABASE_NOT_INITIALIZED.md` - Problemas de BD
3. Ejecuta el script de solución sugerido
4. Si persiste el problema, abre un issue con el reporte adjunto

---

**Última actualización:** 2025-11-19
