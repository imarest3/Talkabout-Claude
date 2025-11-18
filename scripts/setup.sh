#!/bin/bash

# Setup script for Talkabout

echo "=================================="
echo "Talkabout - Setup Script"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env with your configuration before continuing"
    echo ""
    read -p "Press enter to continue after editing .env..."
fi

# Build Docker images
echo ""
echo "Building Docker images..."
docker-compose build

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for database
echo ""
echo "Waiting for database to be ready..."
sleep 10

# Run migrations
echo ""
echo "Running migrations..."
docker-compose exec -T backend python manage.py migrate

# Create superuser
echo ""
echo "Creating superuser..."
echo "You can skip this if you plan to use the init_db script"
read -p "Create superuser now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    docker-compose exec backend python manage.py createsuperuser
fi

# Load sample data
echo ""
read -p "Load sample data for testing? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Loading sample data..."
    docker-compose exec -T backend python manage.py shell < scripts/init_db.py
fi

echo ""
echo "=================================="
echo "Setup complete!"
echo "=================================="
echo ""
echo "Services running:"
echo "  - Backend API: http://localhost:8000"
echo "  - Django Admin: http://localhost:8000/admin"
echo "  - API Docs: http://localhost:8000/api/docs"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Django shell: docker-compose exec backend python manage.py shell"
echo ""
echo "Happy coding! 🚀"
