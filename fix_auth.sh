#!/bin/bash

echo "=================================================="
echo "Solucionando Problemas de Autenticación - Talkabout"
echo "=================================================="
echo ""

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo. Por favor inicia Docker primero."
    exit 1
fi

echo "✓ Docker está corriendo"
echo ""

# Detener servicios
echo "1. Deteniendo servicios..."
docker-compose down

echo ""
echo "2. Iniciando base de datos..."
docker-compose up -d db
echo "   Esperando a que PostgreSQL esté listo..."
sleep 10

echo ""
echo "3. Iniciando backend..."
docker-compose up -d backend
sleep 5

echo ""
echo "4. Aplicando migraciones (incluyendo token_blacklist)..."
docker-compose exec -T backend python manage.py migrate

echo ""
echo "5. Ejecutando diagnóstico de autenticación..."
docker-compose exec -T backend python manage.py shell < scripts/diagnose_auth.py

echo ""
echo "6. Reseteando contraseñas de usuarios de prueba..."
docker-compose exec -T backend python manage.py shell < scripts/init_db.py

echo ""
echo "7. Iniciando todos los servicios..."
docker-compose up -d

sleep 5

echo ""
echo "=================================================="
echo "8. Probando autenticación desde la API..."
echo "=================================================="
echo ""

# Probar login
echo "Intentando login con: student1 / student123"
response=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "student1", "password": "student123"}')

if echo "$response" | grep -q "access"; then
    echo "✅ ¡LOGIN EXITOSO!"
    echo ""
    echo "Tokens recibidos:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
else
    echo "❌ Login falló"
    echo "Respuesta:"
    echo "$response"
fi

echo ""
echo "=================================================="
echo "Solución completada"
echo "=================================================="
echo ""
echo "Servicios disponibles:"
echo "  • Frontend:   http://localhost:3000"
echo "  • Backend:    http://localhost:8000"
echo "  • Admin:      http://localhost:8000/admin"
echo "  • API Docs:   http://localhost:8000/api/docs"
echo ""
echo "Cuentas de prueba:"
echo "  • Admin:      admin / admin123"
echo "  • Profesor:   teacher1 / teacher123"
echo "  • Estudiante: student1 / student123"
echo ""
echo "Si el login aún falla, consulta AUTHENTICATION_TROUBLESHOOTING.md"
echo ""
