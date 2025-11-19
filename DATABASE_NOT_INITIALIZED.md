# 🚨 SOLUCIÓN: Las Tablas No Existen

## El Problema

El error `relation "users_user" does not exist` significa que **las migraciones no se han ejecutado**. La base de datos está vacía.

## ✅ Solución Definitiva (Paso a Paso)

### Opción 1: Script Automático (Más Fácil)

```bash
./setup_from_scratch.sh
```

Este script:
1. ✅ Limpia todo (down -v)
2. ✅ Inicia PostgreSQL y espera que esté listo
3. ✅ Inicia el backend
4. ✅ **CREA las migraciones** (makemigrations)
5. ✅ **APLICA las migraciones** (migrate)
6. ✅ Verifica que las tablas existan
7. ✅ Carga datos de prueba
8. ✅ Prueba el login automáticamente

### Opción 2: Manual (Más Control)

```bash
# 1. Limpiar todo
docker-compose down -v

# 2. Iniciar PostgreSQL
docker-compose up -d db
sleep 15

# 3. Iniciar backend
docker-compose up -d backend
sleep 5

# 4. CREAR migraciones (IMPORTANTE)
docker-compose exec backend python manage.py makemigrations

# 5. APLICAR migraciones
docker-compose exec backend python manage.py migrate

# 6. Verificar que funcionó
docker-compose exec backend python manage.py shell -c "from apps.users.models import User; print('Tablas OK')"

# 7. Cargar datos
docker-compose exec backend python manage.py shell < scripts/init_db.py

# 8. Iniciar todo
docker-compose up -d

# 9. Probar login
curl -X POST http://localhost:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "student1", "password": "student123"}'
```

## 🔍 Por Qué Pasó Esto

Django necesita:
1. **makemigrations**: Crear archivos de migración (Python) basados en los modelos
2. **migrate**: Aplicar esos archivos para crear las tablas en PostgreSQL

Si solo ejecutas `migrate` sin `makemigrations`, Django no sabe qué tablas crear.

## 📝 Comandos Importantes

### Ver si las migraciones existen
```bash
docker-compose exec backend python manage.py showmigrations
```

### Crear migraciones
```bash
docker-compose exec backend python manage.py makemigrations
```

### Aplicar migraciones
```bash
docker-compose exec backend python manage.py migrate
```

### Ver qué tablas hay en la BD
```bash
docker-compose exec backend python manage.py dbshell
\dt
\q
```

## ⚠️ Nota Importante

El error que tuviste es porque:
- ✅ PostgreSQL estaba corriendo
- ✅ Django estaba corriendo
- ❌ **Pero las tablas no existían en la base de datos**

Esto se soluciona ejecutando `makemigrations` + `migrate`.

## 🎯 Ejecuta Esto AHORA

```bash
./setup_from_scratch.sh
```

Espera a que termine (tarda ~1 minuto) y verás si el login funcionó.

Si ves: `✅ ¡LOGIN EXITOSO!` - **¡Problema resuelto!**

Si aún falla, comparte la salida completa del script.
