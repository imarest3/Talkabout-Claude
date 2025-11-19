# Contraseñas y Acceso

## 🔐 Resetear Contraseñas

Si las contraseñas de prueba no funcionan, ejecuta:

```bash
# Opción 1: Ejecutar el script de reset
docker-compose exec backend python manage.py shell < scripts/reset_passwords.py

# Opción 2: Volver a ejecutar init_db (ahora actualiza contraseñas)
docker-compose exec backend python manage.py shell < scripts/init_db.py

# Opción 3: Crear manualmente un superusuario
docker-compose exec backend python manage.py createsuperuser
```

## 👥 Cuentas de Prueba

Después de ejecutar `scripts/init_db.py`:

| Rol | Usuario | Contraseña | Email |
|-----|---------|-----------|-------|
| **Admin** | `admin` | `admin123` | admin@talkabout.com |
| **Profesor** | `teacher1` | `teacher123` | teacher1@talkabout.com |
| **Profesor** | `teacher2` | `teacher123` | teacher2@talkabout.com |
| **Alumno** | `student1` | `student123` | student1@talkabout.com |
| **Alumno** | `student2` | `student123` | student2@talkabout.com |
| ... | ... | ... | ... |
| **Alumno** | `student10` | `student123` | student10@talkabout.com |

## 🚀 Primera Vez - Pasos Completos

Si es tu primera vez usando la aplicación:

```bash
# 1. Iniciar servicios
docker-compose up -d

# 2. Esperar a que la BD esté lista
sleep 10

# 3. Ejecutar migraciones
docker-compose exec backend python manage.py migrate

# 4. Cargar datos de prueba Y establecer contraseñas
docker-compose exec backend python manage.py shell < scripts/init_db.py

# 5. Acceder
# Frontend: http://localhost:3000
# Login: student1 / student123
```

## 🔧 Verificar si un Usuario Existe

```bash
# Entrar a la shell de Django
docker-compose exec backend python manage.py shell

# Dentro de la shell:
from django.contrib.auth import get_user_model
User = get_user_model()

# Ver todos los usuarios
User.objects.all()

# Ver un usuario específico
user = User.objects.get(username='student1')
print(f"Username: {user.username}")
print(f"Email: {user.email}")
print(f"Role: {user.role}")
print(f"Is active: {user.is_active}")

# Resetear contraseña manualmente
user.set_password('student123')
user.save()
print("Password updated!")
```

## 🔑 Crear Tu Propio Usuario Admin

Si prefieres crear tu propio usuario administrador:

```bash
docker-compose exec backend python manage.py createsuperuser

# Te pedirá:
# - Username: (elige el que quieras)
# - Email: (tu email)
# - Password: (tu contraseña)
# - Password (again): (confirmar)
```

Este usuario tendrá acceso completo al sistema.

## 📝 Login desde el Frontend

1. Abre tu navegador en: **http://localhost:3000**
2. Haz clic en "Iniciar Sesión"
3. Ingresa las credenciales:
   - Usuario: `student1`
   - Contraseña: `student123`
4. Haz clic en "Iniciar Sesión"

## 📝 Login al Admin Panel (Django)

1. Abre tu navegador en: **http://localhost:8000/admin**
2. Ingresa las credenciales:
   - Usuario: `admin`
   - Contraseña: `admin123`
3. Desde aquí puedes gestionar todo directamente

## ❓ Solución de Problemas de Login

### Error: "Las credenciales no son válidas"

**Causas posibles:**
1. Las contraseñas no se establecieron correctamente
2. El usuario no existe
3. El usuario está inactivo

**Soluciones:**

```bash
# 1. Verificar que el usuario existe
docker-compose exec backend python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.filter(username='student1').exists()
True

# 2. Resetear contraseña
>>> user = User.objects.get(username='student1')
>>> user.set_password('student123')
>>> user.save()

# 3. Verificar que está activo
>>> user.is_active
True

# Si no está activo:
>>> user.is_active = True
>>> user.save()
```

### Error: "Token inválido" o "No autenticado"

Esto significa que el login funcionó pero hay un problema con los tokens JWT.

**Solución:**
1. Cierra sesión y vuelve a iniciar
2. Limpia el localStorage del navegador (F12 > Application > Local Storage)
3. Verifica que el backend esté corriendo: `docker-compose ps`

### No puedo acceder al Admin Panel

**Asegúrate de que el usuario sea staff:**

```bash
docker-compose exec backend python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> admin = User.objects.get(username='admin')
>>> admin.is_staff = True
>>> admin.is_superuser = True
>>> admin.save()
```

## 🎯 Recomendación

Para una experiencia sin problemas, después de iniciar los servicios por primera vez:

```bash
# Ejecuta esto UNA VEZ
docker-compose exec backend python manage.py shell < scripts/init_db.py
```

Esto creará todos los usuarios con las contraseñas correctas. Si ya ejecutaste el script antes y las contraseñas no funcionan:

```bash
# Ejecuta el script de reset
docker-compose exec backend python manage.py shell < scripts/reset_passwords.py
```

¡Listo! Ahora podrás hacer login sin problemas. 🎉
