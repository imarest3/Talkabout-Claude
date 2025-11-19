#!/bin/bash

# Script de Diagnóstico Completo - Talkabout
# Genera un reporte detallado de todas las fallas y problemas del proyecto

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Contadores de problemas
ERRORS=0
WARNINGS=0
SUCCESS=0

# Timestamp del reporte
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
REPORT_FILE="diagnostic_report_$(date '+%Y%m%d_%H%M%S').log"

# Función para imprimir y guardar en log
log_print() {
    echo -e "$1" | tee -a "$REPORT_FILE"
}

# Función para errores
log_error() {
    ((ERRORS++))
    log_print "${RED}✗ ERROR: $1${NC}"
}

# Función para warnings
log_warning() {
    ((WARNINGS++))
    log_print "${YELLOW}⚠ WARNING: $1${NC}"
}

# Función para success
log_success() {
    ((SUCCESS++))
    log_print "${GREEN}✓ OK: $1${NC}"
}

# Función para info
log_info() {
    log_print "${BLUE}ℹ INFO: $1${NC}"
}

# Función para secciones
log_section() {
    log_print "\n${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_print "${BOLD}$1${NC}"
    log_print "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Iniciar reporte
log_section "DIAGNÓSTICO COMPLETO - PROYECTO TALKABOUT"
log_info "Fecha: $TIMESTAMP"
log_info "Directorio: $(pwd)"
log_info "Usuario: $(whoami)"
echo "" | tee -a "$REPORT_FILE"

# ============================================================
# 1. VERIFICAR ESTRUCTURA DE DIRECTORIOS
# ============================================================
log_section "1. ESTRUCTURA DE DIRECTORIOS Y ARCHIVOS"

# Verificar directorios principales
if [ -d "backend" ]; then
    log_success "Directorio backend/ existe"
else
    log_error "Directorio backend/ NO existe"
fi

if [ -d "frontend" ]; then
    log_success "Directorio frontend/ existe"
else
    log_error "Directorio frontend/ NO existe"
fi

if [ -d "scripts" ]; then
    log_success "Directorio scripts/ existe"
else
    log_error "Directorio scripts/ NO existe"
fi

# Verificar archivos críticos
if [ -f "docker-compose.yml" ]; then
    log_success "Archivo docker-compose.yml existe"
else
    log_error "Archivo docker-compose.yml NO existe"
fi

if [ -f "backend/manage.py" ]; then
    log_success "Archivo backend/manage.py existe"
else
    log_error "Archivo backend/manage.py NO existe - No es un proyecto Django válido"
fi

if [ -f "backend/talkabout/settings.py" ]; then
    log_success "Archivo backend/talkabout/settings.py existe"
else
    log_error "Archivo backend/talkabout/settings.py NO existe"
fi

# ============================================================
# 2. VERIFICAR VARIABLES DE ENTORNO
# ============================================================
log_section "2. VARIABLES DE ENTORNO (.env)"

if [ -f ".env" ]; then
    log_success "Archivo .env existe"

    # Verificar variables críticas
    log_info "Verificando variables críticas en .env:"

    if grep -q "^SECRET_KEY=" .env; then
        log_success "  SECRET_KEY está definida"
    else
        log_error "  SECRET_KEY NO está definida"
    fi

    if grep -q "^DB_NAME=" .env; then
        log_success "  DB_NAME está definida"
    else
        log_warning "  DB_NAME NO está definida (usará default)"
    fi

    if grep -q "^DB_USER=" .env; then
        log_success "  DB_USER está definida"
    else
        log_warning "  DB_USER NO está definida (usará default)"
    fi

    if grep -q "^DB_PASSWORD=" .env; then
        log_success "  DB_PASSWORD está definida"
    else
        log_warning "  DB_PASSWORD NO está definida (usará default)"
    fi

    if grep -q "^DB_HOST=" .env; then
        log_success "  DB_HOST está definida"
    else
        log_warning "  DB_HOST NO está definida (usará default)"
    fi

else
    log_error "Archivo .env NO existe"
    if [ -f ".env.example" ]; then
        log_info "  Archivo .env.example existe - ejecuta: cp .env.example .env"
    else
        log_error "  Archivo .env.example tampoco existe"
    fi
fi

# ============================================================
# 3. VERIFICAR APPS DE DJANGO
# ============================================================
log_section "3. APPS DE DJANGO"

DJANGO_APPS=("users" "activities" "events" "enrollments" "meetings" "statistics")

for app in "${DJANGO_APPS[@]}"; do
    if [ -d "backend/apps/$app" ]; then
        log_success "App '$app' existe"

        # Verificar archivos críticos de la app
        if [ -f "backend/apps/$app/models.py" ]; then
            log_success "  ✓ models.py existe"
        else
            log_error "  ✗ models.py NO existe"
        fi

        if [ -f "backend/apps/$app/__init__.py" ]; then
            log_success "  ✓ __init__.py existe"
        else
            log_warning "  ⚠ __init__.py NO existe"
        fi

        if [ -f "backend/apps/$app/apps.py" ]; then
            log_success "  ✓ apps.py existe"
        else
            log_warning "  ⚠ apps.py NO existe"
        fi

    else
        log_error "App '$app' NO existe en backend/apps/"
    fi
done

# ============================================================
# 4. VERIFICAR MIGRACIONES
# ============================================================
log_section "4. MIGRACIONES DE DJANGO"

for app in "${DJANGO_APPS[@]}"; do
    if [ -d "backend/apps/$app/migrations" ]; then
        log_success "Directorio migrations/ existe para '$app'"

        # Contar archivos de migración
        migration_count=$(ls -1 backend/apps/$app/migrations/*.py 2>/dev/null | grep -v "__init__.py" | wc -l)
        if [ "$migration_count" -gt 0 ]; then
            log_info "  Archivos de migración encontrados: $migration_count"
        else
            log_warning "  No hay archivos de migración (solo __init__.py)"
        fi
    else
        log_error "Directorio migrations/ NO existe para '$app'"
        log_info "  Ejecutar: docker-compose exec backend python manage.py makemigrations $app"
    fi
done

# ============================================================
# 5. VERIFICAR DOCKER
# ============================================================
log_section "5. DOCKER Y CONTENEDORES"

# Verificar si Docker está instalado
if command -v docker &> /dev/null; then
    log_success "Docker está instalado"

    # Verificar si Docker está corriendo
    if docker info &> /dev/null; then
        log_success "Docker daemon está corriendo"

        # Verificar contenedores
        log_info "Estado de contenedores:"
        docker-compose ps 2>&1 | tee -a "$REPORT_FILE"

        # Verificar contenedores específicos
        if docker-compose ps | grep -q "db.*Up"; then
            log_success "  Contenedor 'db' está corriendo"
        else
            log_error "  Contenedor 'db' NO está corriendo"
        fi

        if docker-compose ps | grep -q "backend.*Up"; then
            log_success "  Contenedor 'backend' está corriendo"
        else
            log_error "  Contenedor 'backend' NO está corriendo"
        fi

        if docker-compose ps | grep -q "redis.*Up"; then
            log_success "  Contenedor 'redis' está corriendo"
        else
            log_warning "  Contenedor 'redis' NO está corriendo"
        fi

    else
        log_error "Docker daemon NO está corriendo"
        log_info "  Ejecutar: sudo systemctl start docker (Linux) o iniciar Docker Desktop"
    fi
else
    log_error "Docker NO está instalado"
    log_info "  Instalar desde: https://docs.docker.com/get-docker/"
fi

# Verificar docker-compose
if command -v docker-compose &> /dev/null; then
    log_success "docker-compose está instalado"
    version=$(docker-compose --version)
    log_info "  Versión: $version"
else
    log_error "docker-compose NO está instalado"
fi

# ============================================================
# 6. VERIFICAR BASE DE DATOS (SI DOCKER ESTÁ CORRIENDO)
# ============================================================
log_section "6. BASE DE DATOS POSTGRESQL"

if command -v docker &> /dev/null && docker info &> /dev/null; then
    if docker-compose ps | grep -q "db.*Up"; then
        log_info "Intentando conectar a PostgreSQL..."

        # Verificar conexión a PostgreSQL
        if docker-compose exec -T db pg_isready -U talkabout_user -d talkabout &> /dev/null; then
            log_success "PostgreSQL está respondiendo"

            # Verificar si las tablas existen
            log_info "Verificando tablas en la base de datos..."

            table_check=$(docker-compose exec -T db psql -U talkabout_user -d talkabout -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>&1)

            if [[ "$table_check" =~ [0-9]+ ]]; then
                table_count=$(echo "$table_check" | tr -d ' ')
                log_info "  Número de tablas en la BD: $table_count"

                if [ "$table_count" -eq 0 ]; then
                    log_error "  La base de datos está vacía - NO hay tablas"
                    log_info "  Ejecutar: docker-compose exec backend python manage.py migrate"
                fi

                # Verificar tabla users_user específicamente
                user_table_check=$(docker-compose exec -T db psql -U talkabout_user -d talkabout -t -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users_user');" 2>&1)

                if echo "$user_table_check" | grep -q "t"; then
                    log_success "  Tabla 'users_user' existe"
                else
                    log_error "  Tabla 'users_user' NO existe"
                    log_info "  Este es el error: django.db.utils.ProgrammingError: relation 'users_user' does not exist"
                fi

                # Listar algunas tablas si existen
                if [ "$table_count" -gt 0 ]; then
                    log_info "  Tablas encontradas:"
                    docker-compose exec -T db psql -U talkabout_user -d talkabout -t -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;" 2>&1 | head -20 | tee -a "$REPORT_FILE"
                fi
            else
                log_warning "  No se pudo obtener el conteo de tablas"
            fi

        else
            log_error "PostgreSQL NO está respondiendo"
        fi
    else
        log_warning "Contenedor de base de datos no está corriendo - omitiendo verificación de BD"
    fi
else
    log_warning "Docker no está disponible - omitiendo verificación de BD"
fi

# ============================================================
# 7. VERIFICAR CONFIGURACIÓN DE DJANGO
# ============================================================
log_section "7. CONFIGURACIÓN DE DJANGO (settings.py)"

if [ -f "backend/talkabout/settings.py" ]; then
    log_info "Verificando configuraciones críticas..."

    # Verificar AUTH_USER_MODEL
    if grep -q "AUTH_USER_MODEL.*=.*'users.User'" backend/talkabout/settings.py; then
        log_success "AUTH_USER_MODEL está configurado correctamente ('users.User')"
    else
        log_error "AUTH_USER_MODEL NO está configurado o es incorrecto"
    fi

    # Verificar apps instaladas
    if grep -q "'apps.users'" backend/talkabout/settings.py; then
        log_success "App 'apps.users' está en INSTALLED_APPS"
    else
        log_error "App 'apps.users' NO está en INSTALLED_APPS"
    fi

    if grep -q "'rest_framework'" backend/talkabout/settings.py; then
        log_success "rest_framework está en INSTALLED_APPS"
    else
        log_warning "rest_framework NO está en INSTALLED_APPS"
    fi

    if grep -q "'rest_framework_simplejwt'" backend/talkabout/settings.py; then
        log_success "rest_framework_simplejwt está en INSTALLED_APPS"
    else
        log_warning "rest_framework_simplejwt NO está en INSTALLED_APPS"
    fi

    if grep -q "'corsheaders'" backend/talkabout/settings.py; then
        log_success "corsheaders está en INSTALLED_APPS"
    else
        log_warning "corsheaders NO está en INSTALLED_APPS"
    fi

    # Verificar configuración de BD
    if grep -q "DATABASES" backend/talkabout/settings.py; then
        log_success "Configuración DATABASES existe"

        if grep -q "django.db.backends.postgresql" backend/talkabout/settings.py; then
            log_success "  Motor PostgreSQL configurado"
        else
            log_warning "  Motor de BD no es PostgreSQL"
        fi
    else
        log_error "Configuración DATABASES NO existe"
    fi
fi

# ============================================================
# 8. VERIFICAR DEPENDENCIAS PYTHON
# ============================================================
log_section "8. DEPENDENCIAS PYTHON"

if [ -f "backend/requirements.txt" ]; then
    log_success "Archivo requirements.txt existe"

    log_info "Dependencias críticas:"
    if grep -q "^Django" backend/requirements.txt; then
        log_success "  Django está listado"
    else
        log_error "  Django NO está listado"
    fi

    if grep -q "djangorestframework" backend/requirements.txt; then
        log_success "  djangorestframework está listado"
    else
        log_warning "  djangorestframework NO está listado"
    fi

    if grep -q "psycopg2" backend/requirements.txt; then
        log_success "  psycopg2 (PostgreSQL adapter) está listado"
    else
        log_error "  psycopg2 NO está listado"
    fi
else
    log_error "Archivo requirements.txt NO existe"
fi

# ============================================================
# 9. VERIFICAR LOGS DE DOCKER (SI ESTÁ DISPONIBLE)
# ============================================================
log_section "9. ÚLTIMOS LOGS DEL BACKEND (si disponible)"

if command -v docker &> /dev/null && docker info &> /dev/null; then
    if docker-compose ps | grep -q "backend"; then
        log_info "Últimos 30 logs del backend:"
        echo "----------------------------------------" | tee -a "$REPORT_FILE"
        docker-compose logs --tail=30 backend 2>&1 | tee -a "$REPORT_FILE"
        echo "----------------------------------------" | tee -a "$REPORT_FILE"
    else
        log_warning "Backend no está corriendo - no hay logs disponibles"
    fi
else
    log_warning "Docker no disponible - no se pueden leer logs"
fi

# ============================================================
# 10. VERIFICAR SCRIPTS DE SOLUCIÓN
# ============================================================
log_section "10. SCRIPTS DE SOLUCIÓN DISPONIBLES"

if [ -f "setup_from_scratch.sh" ]; then
    log_success "Script setup_from_scratch.sh existe"
    if [ -x "setup_from_scratch.sh" ]; then
        log_success "  ✓ Es ejecutable"
    else
        log_warning "  ⚠ NO es ejecutable - ejecutar: chmod +x setup_from_scratch.sh"
    fi
else
    log_warning "Script setup_from_scratch.sh NO existe"
fi

if [ -f "fix_auth.sh" ]; then
    log_success "Script fix_auth.sh existe"
    if [ -x "fix_auth.sh" ]; then
        log_success "  ✓ Es ejecutable"
    else
        log_warning "  ⚠ NO es ejecutable - ejecutar: chmod +x fix_auth.sh"
    fi
else
    log_warning "Script fix_auth.sh NO existe"
fi

if [ -f "scripts/init_db.py" ]; then
    log_success "Script scripts/init_db.py existe"
else
    log_warning "Script scripts/init_db.py NO existe"
fi

# ============================================================
# RESUMEN FINAL
# ============================================================
log_section "RESUMEN DEL DIAGNÓSTICO"

log_print ""
log_print "${BOLD}Estadísticas:${NC}"
log_print "${GREEN}  ✓ Verificaciones exitosas: $SUCCESS${NC}"
log_print "${YELLOW}  ⚠ Advertencias: $WARNINGS${NC}"
log_print "${RED}  ✗ Errores críticos: $ERRORS${NC}"
log_print ""

# Determinar el problema principal
log_section "DIAGNÓSTICO PRINCIPAL"

if [ $ERRORS -gt 0 ]; then
    log_print "${RED}${BOLD}⚠ SE ENCONTRARON PROBLEMAS CRÍTICOS${NC}"
    log_print ""

    # Identificar el problema más probable
    if [ ! -d "backend/apps/users/migrations" ]; then
        log_print "${YELLOW}${BOLD}PROBLEMA PRINCIPAL IDENTIFICADO:${NC}"
        log_print "  ${RED}✗ No existen directorios de migraciones${NC}"
        log_print ""
        log_print "${BOLD}CAUSA DEL ERROR:${NC}"
        log_print "  django.db.utils.ProgrammingError: relation 'users_user' does not exist"
        log_print ""
        log_print "${BOLD}SOLUCIÓN:${NC}"
        log_print "  1. Ejecutar: ${GREEN}./setup_from_scratch.sh${NC}"
        log_print "  O manualmente:"
        log_print "  2. docker-compose up -d db backend"
        log_print "  3. docker-compose exec backend python manage.py makemigrations"
        log_print "  4. docker-compose exec backend python manage.py migrate"
        log_print "  5. docker-compose exec backend python manage.py shell < scripts/init_db.py"
    elif [ ! -f ".env" ]; then
        log_print "${YELLOW}${BOLD}PROBLEMA PRINCIPAL IDENTIFICADO:${NC}"
        log_print "  ${RED}✗ Archivo .env no existe${NC}"
        log_print ""
        log_print "${BOLD}SOLUCIÓN:${NC}"
        log_print "  1. Ejecutar: ${GREEN}cp .env.example .env${NC}"
        log_print "  2. Editar .env con tus configuraciones"
        log_print "  3. Ejecutar: ${GREEN}./setup_from_scratch.sh${NC}"
    fi
else
    log_print "${GREEN}${BOLD}✓ No se encontraron problemas críticos${NC}"
fi

log_print ""
log_print "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
log_print "${BOLD}Reporte completo guardado en: ${BLUE}$REPORT_FILE${NC}"
log_print "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
log_print ""

# Salir con código de error si hay errores críticos
if [ $ERRORS -gt 0 ]; then
    exit 1
else
    exit 0
fi
