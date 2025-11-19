#!/bin/bash

echo "================================================"
echo "Talkabout - Script de Inicio Rápido"
echo "================================================"
echo ""

# Verificar que Docker esté corriendo
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker no está corriendo. Por favor inicia Docker primero."
    exit 1
fi

echo "✓ Docker está corriendo"
echo ""

# Parar contenedores existentes si los hay
echo "Deteniendo contenedores existentes (si los hay)..."
docker-compose down

echo ""
echo "Construyendo imágenes Docker..."
docker-compose build

echo ""
echo "Iniciando servicios..."
docker-compose up -d

echo ""
echo "Esperando a que los servicios estén listos..."
sleep 10

echo ""
echo "Ejecutando migraciones de base de datos..."
docker-compose exec -T backend python manage.py migrate

echo ""
read -p "¿Quieres cargar datos de prueba? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]
then
    echo "Cargando datos de prueba..."
    docker-compose exec -T backend python manage.py shell < scripts/init_db.py
    echo ""
    echo "✓ Datos de prueba cargados"
    echo ""
    echo "Cuentas disponibles:"
    echo "  Admin:    admin / admin123"
    echo "  Profesor: teacher1 / teacher123"
    echo "  Alumno:   student1 / student123"
fi

echo ""
echo "================================================"
echo "✓ ¡Talkabout está listo!"
echo "================================================"
echo ""
echo "Servicios disponibles:"
echo "  • Frontend:   http://localhost:3000"
echo "  • Backend:    http://localhost:8000"
echo "  • Admin:      http://localhost:8000/admin"
echo "  • API Docs:   http://localhost:8000/api/docs"
echo ""
echo "Comandos útiles:"
echo "  • Ver logs:         docker-compose logs -f"
echo "  • Detener todo:     docker-compose down"
echo "  • Reiniciar:        docker-compose restart"
echo "  • Django shell:     docker-compose exec backend python manage.py shell"
echo ""
echo "¡Disfruta de Talkabout! 🚀"
