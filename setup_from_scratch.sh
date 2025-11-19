#!/bin/bash

echo "============================================================"
echo "SOLUCIÓN COMPLETA - Inicialización desde Cero"
echo "============================================================"
echo ""

# Verificar Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo"
    exit 1
fi

echo "✓ Docker está corriendo"
echo ""

# Paso 1: Limpiar todo
echo "1. Limpiando servicios y volúmenes anteriores..."
docker-compose down -v
echo "   ✓ Servicios detenidos y volúmenes eliminados"
echo ""

# Paso 2: Iniciar solo la base de datos
echo "2. Iniciando PostgreSQL..."
docker-compose up -d db
echo "   Esperando 15 segundos a que PostgreSQL esté completamente listo..."
sleep 15

# Verificar que PostgreSQL esté listo
echo "   Verificando PostgreSQL..."
docker-compose exec db pg_isready -U talkabout_user -d talkabout
if [ $? -eq 0 ]; then
    echo "   ✓ PostgreSQL está listo"
else
    echo "   ⚠️  PostgreSQL no responde, esperando 10 segundos más..."
    sleep 10
fi
echo ""

# Paso 3: Iniciar backend
echo "3. Iniciando backend..."
docker-compose up -d backend
sleep 5
echo "   ✓ Backend iniciado"
echo ""

# Paso 4: Crear migraciones
echo "4. Creando migraciones de Django..."
docker-compose exec -T backend python manage.py makemigrations
echo "   ✓ Migraciones creadas"
echo ""

# Paso 5: Aplicar migraciones
echo "5. Aplicando migraciones a la base de datos..."
docker-compose exec -T backend python manage.py migrate
echo "   ✓ Migraciones aplicadas"
echo ""

# Paso 6: Verificar tablas
echo "6. Verificando que las tablas se crearon..."
docker-compose exec -T backend python manage.py shell <<EOF
from django.db import connection
tables = connection.introspection.table_names()
print(f"Tablas creadas: {len(tables)}")
if 'users_user' in tables:
    print("✓ Tabla users_user existe")
else:
    print("✗ Tabla users_user NO existe")
EOF
echo ""

# Paso 7: Cargar datos de prueba
echo "7. Cargando usuarios y datos de prueba..."
docker-compose exec -T backend python manage.py shell < scripts/init_db.py
echo ""

# Paso 8: Iniciar todos los servicios
echo "8. Iniciando todos los servicios..."
docker-compose up -d
sleep 5
echo "   ✓ Todos los servicios iniciados"
echo ""

# Paso 9: Verificar servicios
echo "9. Verificando estado de servicios..."
docker-compose ps
echo ""

# Paso 10: Probar autenticación
echo "============================================================"
echo "10. PRUEBA DE AUTENTICACIÓN"
echo "============================================================"
echo ""
echo "Probando login con: student1 / student123"
echo ""

sleep 3

response=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8000/api/auth/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username": "student1", "password": "student123"}')

http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "✅ ¡LOGIN EXITOSO!"
    echo ""
    echo "Tokens JWT recibidos:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    echo ""
    echo "============================================================"
    echo "🎉 ¡TODO FUNCIONANDO CORRECTAMENTE!"
    echo "============================================================"
elif [ "$http_code" = "000" ]; then
    echo "❌ No se pudo conectar al backend"
    echo ""
    echo "El backend puede no estar listo aún. Espera 30 segundos y ejecuta:"
    echo "curl -X POST http://localhost:8000/api/auth/token/ \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"username\": \"student1\", \"password\": \"student123\"}'"
else
    echo "❌ Login falló (HTTP $http_code)"
    echo ""
    echo "Respuesta:"
    echo "$body"
    echo ""
    echo "Verificando logs del backend..."
    docker-compose logs backend --tail 20
fi

echo ""
echo "============================================================"
echo "Información de Acceso"
echo "============================================================"
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
echo "Comandos útiles:"
echo "  • Ver logs:        docker-compose logs -f backend"
echo "  • Ver todos:       docker-compose logs -f"
echo "  • Reiniciar:       docker-compose restart"
echo "  • Detener:         docker-compose down"
echo ""
