"""
Script para resetear contraseñas de usuarios de prueba.
Ejecutar con: docker-compose exec backend python manage.py shell < scripts/reset_passwords.py
"""
from django.contrib.auth import get_user_model

User = get_user_model()

print("Reseteando contraseñas de usuarios de prueba...")
print("=" * 50)

# Reset admin password
try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')
    admin.save()
    print("✓ Admin password reset: admin / admin123")
except User.DoesNotExist:
    print("✗ Usuario 'admin' no existe")

# Reset teacher1 password
try:
    teacher1 = User.objects.get(username='teacher1')
    teacher1.set_password('teacher123')
    teacher1.save()
    print("✓ Teacher1 password reset: teacher1 / teacher123")
except User.DoesNotExist:
    print("✗ Usuario 'teacher1' no existe")

# Reset teacher2 password
try:
    teacher2 = User.objects.get(username='teacher2')
    teacher2.set_password('teacher123')
    teacher2.save()
    print("✓ Teacher2 password reset: teacher2 / teacher123")
except User.DoesNotExist:
    print("✗ Usuario 'teacher2' no existe")

# Reset students passwords
for i in range(1, 11):
    try:
        student = User.objects.get(username=f'student{i}')
        student.set_password('student123')
        student.save()
        print(f"✓ Student{i} password reset: student{i} / student123")
    except User.DoesNotExist:
        print(f"✗ Usuario 'student{i}' no existe")

print("=" * 50)
print("\n✓ Contraseñas reseteadas exitosamente!")
print("\nPuedes hacer login con:")
print("  Admin:    admin / admin123")
print("  Profesor: teacher1 / teacher123")
print("  Alumno:   student1 / student123")
