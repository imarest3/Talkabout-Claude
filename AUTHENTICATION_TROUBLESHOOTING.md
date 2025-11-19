# Análisis del Problema de Autenticación

## 🔍 Problemas Identificados

### 1. **App JWT Blacklist Faltante** ⚠️ CRÍTICO

**Problema:**
El archivo `settings.py` tiene configurado `BLACKLIST_AFTER_ROTATION = True` pero falta la app necesaria en `INSTALLED_APPS`.

**Consecuencia:**
Esto puede causar errores al intentar hacer login o logout.

**Solución Aplicada:**
```python
# En backend/talkabout/settings.py
INSTALLED_APPS = [
    ...
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',  # ✅ Añadido
    ...
]
```

### 2. **Posibles Problemas con Contraseñas**

El script `init_db.py` usa `get_or_create()` que solo establece contraseñas en la creación inicial.

**Ya corregido en el commit anterior.**

## 🛠️ Pasos para Solucionar

### Paso 1: Aplicar la Migración de Blacklist

Después de corregir el código, debes aplicar las migraciones:

```bash
# Detener servicios
docker-compose down

# Iniciar solo la base de datos
docker-compose up -d db
sleep 5

# Iniciar backend y aplicar migraciones
docker-compose up -d backend
docker-compose exec backend python manage.py migrate

# Iniciar todos los servicios
docker-compose up -d
```

### Paso 2: Ejecutar Script de Diagnóstico

```bash
docker-compose exec backend python manage.py shell < scripts/diagnose_auth.py
```

Este script:
- ✅ Verifica todos los usuarios
- ✅ Prueba autenticación con cada usuario
- ✅ Detecta contraseñas incorrectas y las resetea automáticamente
- ✅ Muestra configuración de JWT
- ✅ Verifica apps instaladas

### Paso 3: Resetear Contraseñas

```bash
docker-compose exec backend python manage.py shell < scripts/init_db.py
```

### Paso 4: Probar Login desde la Terminal

```bash
# Probar login con curl
curl -X POST http://localhost:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "student1", "password": "student123"}'
```

**Respuesta esperada:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Si hay error:**
```json
{
  "detail": "No active account found with the given credentials"
}
```

## 🔧 Comandos de Diagnóstico Manual

### Verificar Usuario en la Base de Datos

```bash
docker-compose exec backend python manage.py shell

# Dentro de la shell:
from django.contrib.auth import get_user_model
User = get_user_model()

# Ver usuario
user = User.objects.get(username='student1')
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Is active: {user.is_active}")
print(f"Has password: {user.has_usable_password()}")

# Probar contraseña
print(user.check_password('student123'))  # Debe retornar True

# Si retorna False, resetear:
user.set_password('student123')
user.save()
print("Contraseña reseteada")
```

### Verificar Autenticación Django

```bash
docker-compose exec backend python manage.py shell

from django.contrib.auth import authenticate

# Probar autenticación
user = authenticate(username='student1', password='student123')
if user:
    print(f"✓ Autenticación exitosa: {user.username}")
else:
    print("✗ Autenticación fallida")
```

### Verificar Logs del Backend

```bash
# Ver logs en tiempo real
docker-compose logs -f backend

# Ver últimas 100 líneas
docker-compose logs backend --tail 100

# Buscar errores
docker-compose logs backend | grep -i error
```

## 📊 Posibles Causas del Problema

### Causa 1: App token_blacklist no instalada
**Síntoma:** Error al hacer login o logout
**Solución:** Añadir 'rest_framework_simplejwt.token_blacklist' a INSTALLED_APPS

### Causa 2: Contraseñas no hasheadas correctamente
**Síntoma:** check_password retorna False
**Solución:** Ejecutar init_db.py o reset_passwords.py

### Causa 3: Usuario no existe
**Síntoma:** DoesNotExist exception
**Solución:** Ejecutar init_db.py para crear usuarios

### Causa 4: Usuario inactivo
**Síntoma:** "No active account found"
**Solución:**
```python
user.is_active = True
user.save()
```

### Causa 5: Problema con CORS
**Síntoma:** Error de red en el frontend
**Solución:** Verificar CORS_ALLOWED_ORIGINS en settings.py

### Causa 6: Base de datos no inicializada
**Síntoma:** Tabla User no existe
**Solución:**
```bash
docker-compose exec backend python manage.py migrate
```

## ✅ Checklist de Verificación

- [ ] ¿docker-compose ps muestra todos los servicios running?
- [ ] ¿Las migraciones están aplicadas?
- [ ] ¿El usuario existe en la BD?
- [ ] ¿El usuario está activo (is_active=True)?
- [ ] ¿La contraseña está hasheada correctamente?
- [ ] ¿token_blacklist está en INSTALLED_APPS?
- [ ] ¿El backend responde en localhost:8000?
- [ ] ¿El frontend puede conectarse al backend?
- [ ] ¿CORS está configurado correctamente?

## 🎯 Script Completo de Solución

```bash
#!/bin/bash

echo "Solucionando problemas de autenticación..."

# 1. Reiniciar servicios
docker-compose down
docker-compose up -d

# 2. Esperar a que la BD esté lista
sleep 10

# 3. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 4. Ejecutar diagnóstico
docker-compose exec backend python manage.py shell < scripts/diagnose_auth.py

# 5. Resetear contraseñas
docker-compose exec backend python manage.py shell < scripts/init_db.py

# 6. Probar login
echo ""
echo "Probando login..."
curl -X POST http://localhost:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "student1", "password": "student123"}'

echo ""
echo "Listo! Intenta hacer login en http://localhost:3000"
```

## 📞 Si Aún No Funciona

1. Comparte la salida del script de diagnóstico
2. Comparte los logs: `docker-compose logs backend --tail 50`
3. Intenta crear un superusuario manualmente y hacer login con él
4. Verifica que el frontend esté llamando a la URL correcta
