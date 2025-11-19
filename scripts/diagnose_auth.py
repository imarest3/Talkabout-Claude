"""
Script de diagnóstico para el sistema de autenticación.
Ejecutar con: docker-compose exec backend python manage.py shell < scripts/diagnose_auth.py
"""
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password

User = get_user_model()

print("="*60)
print("DIAGNÓSTICO DEL SISTEMA DE AUTENTICACIÓN")
print("="*60)

# 1. Verificar usuarios
print("\n1. USUARIOS EN LA BASE DE DATOS:")
print("-" * 60)
users = User.objects.all()
print(f"Total de usuarios: {users.count()}")

for user in users[:5]:  # Mostrar primeros 5
    print(f"\n  Usuario: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {user.role}")
    print(f"  Is active: {user.is_active}")
    print(f"  Is staff: {user.is_staff}")
    print(f"  Has usable password: {user.has_usable_password()}")

# 2. Probar autenticación manual
print("\n" + "="*60)
print("2. PRUEBA DE AUTENTICACIÓN MANUAL:")
print("-" * 60)

test_users = ['admin', 'teacher1', 'student1']
test_password = {
    'admin': 'admin123',
    'teacher1': 'teacher123',
    'student1': 'student123'
}

for username in test_users:
    try:
        user = User.objects.get(username=username)
        password = test_password[username]

        print(f"\nProbando: {username} / {password}")

        # Método 1: check_password directo
        is_valid_direct = user.check_password(password)
        print(f"  ✓ check_password directo: {is_valid_direct}")

        # Método 2: authenticate de Django
        auth_user = authenticate(username=username, password=password)
        print(f"  ✓ authenticate: {'OK' if auth_user else 'FAIL'}")

        # Mostrar hash
        print(f"  Password hash: {user.password[:50]}...")

        if not is_valid_direct:
            print(f"  ⚠️  CONTRASEÑA INCORRECTA - Reseteando...")
            user.set_password(password)
            user.save()
            print(f"  ✓ Contraseña reseteada")

            # Verificar de nuevo
            if user.check_password(password):
                print(f"  ✓ Verificación post-reset: OK")
            else:
                print(f"  ✗ Verificación post-reset: FAIL")
    except User.DoesNotExist:
        print(f"\n✗ Usuario '{username}' NO EXISTE")

# 3. Verificar configuración de JWT
print("\n" + "="*60)
print("3. CONFIGURACIÓN JWT:")
print("-" * 60)

from django.conf import settings

print(f"  AUTH_USER_MODEL: {settings.AUTH_USER_MODEL}")
print(f"  REST_FRAMEWORK authentication:")
for auth in settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', []):
    print(f"    - {auth}")

if hasattr(settings, 'SIMPLE_JWT'):
    print(f"\n  SIMPLE_JWT configurado:")
    print(f"    - ACCESS_TOKEN_LIFETIME: {settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')}")
    print(f"    - ALGORITHM: {settings.SIMPLE_JWT.get('ALGORITHM')}")
    print(f"    - BLACKLIST_AFTER_ROTATION: {settings.SIMPLE_JWT.get('BLACKLIST_AFTER_ROTATION')}")

# 4. Verificar apps instaladas
print("\n" + "="*60)
print("4. APPS RELACIONADAS CON AUTH:")
print("-" * 60)

auth_apps = [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'apps.users'
]

for app in auth_apps:
    if app in settings.INSTALLED_APPS:
        print(f"  ✓ {app}")
    else:
        print(f"  ✗ {app} - NO INSTALADA")

print("\n" + "="*60)
print("DIAGNÓSTICO COMPLETADO")
print("="*60)

# Sugerencias
print("\nSUGERENCIAS:")
if not any('token_blacklist' in app for app in settings.INSTALLED_APPS):
    print("  ⚠️  Añadir 'rest_framework_simplejwt.token_blacklist' a INSTALLED_APPS")

print("\nPara probar el login desde la API:")
print("  curl -X POST http://localhost:8000/api/auth/token/ \\")
print("    -H 'Content-Type: application/json' \\")
print("    -d '{\"username\": \"student1\", \"password\": \"student123\"}'")
