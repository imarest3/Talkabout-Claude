"""
Script to initialize database with sample data for testing.
Run with: python manage.py shell < scripts/init_db.py
"""
from django.contrib.auth import get_user_model
from apps.activities.models import Activity
from apps.events.models import Event
from apps.enrollments.models import Enrollment
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

print("Creating sample users...")

# Create admin
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@talkabout.com',
        'role': User.Role.ADMIN,
        'first_name': 'Admin',
        'last_name': 'User',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print(f"✓ Created admin user: {admin.username}")

# Create teachers
teacher1, created = User.objects.get_or_create(
    username='teacher1',
    defaults={
        'email': 'teacher1@talkabout.com',
        'role': User.Role.TEACHER,
        'first_name': 'María',
        'last_name': 'García'
    }
)
if created:
    teacher1.set_password('teacher123')
    teacher1.save()
    print(f"✓ Created teacher: {teacher1.username}")

teacher2, created = User.objects.get_or_create(
    username='teacher2',
    defaults={
        'email': 'teacher2@talkabout.com',
        'role': User.Role.TEACHER,
        'first_name': 'Juan',
        'last_name': 'Martínez'
    }
)
if created:
    teacher2.set_password('teacher123')
    teacher2.save()
    print(f"✓ Created teacher: {teacher2.username}")

# Create students
students = []
for i in range(1, 11):
    student, created = User.objects.get_or_create(
        username=f'student{i}',
        defaults={
            'email': f'student{i}@talkabout.com',
            'role': User.Role.STUDENT,
            'first_name': f'Estudiante',
            'last_name': f'{i}'
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print(f"✓ Created student: {student.username}")
    students.append(student)

print("\nCreating sample activities...")

# Activity 1
activity1, created = Activity.objects.get_or_create(
    title='Conversación en Español - Nivel Intermedio',
    defaults={
        'description': """
Practica tu español en una conversación grupal sobre temas cotidianos.
En esta sesión hablaremos sobre:
- Hobbies y tiempo libre
- Experiencias de viaje
- Comida y gastronomía

Nivel requerido: B1-B2
""",
        'created_by': teacher1,
        'max_participants_per_meeting': 6,
        'min_participants_per_meeting': 3
    }
)
if created:
    print(f"✓ Created activity: {activity1.title}")

# Activity 2
activity2, created = Activity.objects.get_or_create(
    title='English Conversation - Business Topics',
    defaults={
        'description': """
Practice English conversation focused on business and professional topics.
Topics include:
- Presentations and meetings
- Negotiations
- Email communication
- Networking

Level required: B2-C1
""",
        'created_by': teacher2,
        'max_participants_per_meeting': 8,
        'min_participants_per_meeting': 4
    }
)
if created:
    print(f"✓ Created activity: {activity2.title}")

print("\nCreating sample events...")

now = timezone.now()

# Events for Activity 1
events1 = []
for i in range(3):
    start_time = now + timedelta(days=i+1, hours=10)
    end_time = start_time + timedelta(hours=1)

    event, created = Event.objects.get_or_create(
        activity=activity1,
        start_time=start_time,
        defaults={
            'end_time': end_time
        }
    )
    if created:
        print(f"✓ Created event for {activity1.title}: {start_time.strftime('%Y-%m-%d %H:%M')}")
        events1.append(event)

# Events for Activity 2
events2 = []
for i in range(2):
    start_time = now + timedelta(days=i+2, hours=15)
    end_time = start_time + timedelta(hours=1, minutes=30)

    event, created = Event.objects.get_or_create(
        activity=activity2,
        start_time=start_time,
        defaults={
            'end_time': end_time
        }
    )
    if created:
        print(f"✓ Created event for {activity2.title}: {start_time.strftime('%Y-%m-%d %H:%M')}")
        events2.append(event)

print("\nCreating sample enrollments...")

# Enroll students in events
import random

for event in events1:
    # Randomly enroll 4-7 students
    num_enrollments = random.randint(4, 7)
    enrolled_students = random.sample(students, num_enrollments)

    for student in enrolled_students:
        enrollment, created = Enrollment.objects.get_or_create(
            user=student,
            event=event
        )
        if created:
            print(f"✓ Enrolled {student.username} in event {event.id}")

for event in events2:
    # Randomly enroll 5-8 students
    num_enrollments = random.randint(5, 8)
    enrolled_students = random.sample(students, num_enrollments)

    for student in enrolled_students:
        enrollment, created = Enrollment.objects.get_or_create(
            user=student,
            event=event
        )
        if created:
            print(f"✓ Enrolled {student.username} in event {event.id}")

print("\n" + "="*50)
print("Database initialized successfully!")
print("="*50)
print("\nTest accounts:")
print(f"Admin:    username=admin    password=admin123")
print(f"Teacher:  username=teacher1 password=teacher123")
print(f"Student:  username=student1 password=student123")
print("\nAccess:")
print(f"API: http://localhost:8000/api/")
print(f"Admin: http://localhost:8000/admin/")
print(f"Docs: http://localhost:8000/api/docs/")
