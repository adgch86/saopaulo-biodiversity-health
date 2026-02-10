#!/bin/bash
# TerraRisk Workshop - Deploy Script
# Usage: ./deploy.sh [start|stop|restart|rebuild|logs|status]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Config
COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="terrarisk-workshop"

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado"
        exit 1
    fi
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose no está instalado"
        exit 1
    fi
    print_success "Docker y Docker Compose detectados"
}

# Start services
start() {
    print_header "Iniciando TerraRisk Workshop"

    check_docker

    print_info "Building imágenes Docker..."
    docker-compose -f $COMPOSE_FILE build

    print_info "Levantando servicios..."
    docker-compose -f $COMPOSE_FILE up -d

    print_success "Servicios iniciados"

    sleep 5
    status

    print_info "\nVerificando health del backend..."
    if curl -sf http://localhost:8002/api/health > /dev/null; then
        print_success "Backend API está healthy"
    else
        print_warning "Backend API no responde aún, puede tardar unos segundos"
    fi

    print_info "\nURLs de acceso:"
    echo "  - Frontend: http://localhost:4001"
    echo "  - Backend API: http://localhost:8002/api/health"
    echo "  - Público: https://terrarisk.arlexperalta.com (requiere Nginx Proxy Manager)"
}

# Stop services
stop() {
    print_header "Deteniendo TerraRisk Workshop"

    docker-compose -f $COMPOSE_FILE stop

    print_success "Servicios detenidos"
}

# Restart services
restart() {
    print_header "Reiniciando TerraRisk Workshop"

    stop
    sleep 2
    start
}

# Rebuild from scratch
rebuild() {
    print_header "Rebuild Completo (sin caché)"

    print_warning "Esto detendrá los servicios y reconstruirá las imágenes desde cero"
    read -p "¿Continuar? (y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Operación cancelada"
        exit 0
    fi

    print_info "Deteniendo servicios..."
    docker-compose -f $COMPOSE_FILE down

    print_info "Limpiando imágenes antiguas..."
    docker-compose -f $COMPOSE_FILE build --no-cache

    print_info "Levantando servicios..."
    docker-compose -f $COMPOSE_FILE up -d

    print_success "Rebuild completo exitoso"

    sleep 5
    status
}

# Show logs
logs() {
    print_header "Logs de TerraRisk Workshop"

    if [ -z "$2" ]; then
        docker-compose -f $COMPOSE_FILE logs -f
    else
        docker-compose -f $COMPOSE_FILE logs -f $2
    fi
}

# Show status
status() {
    print_header "Estado de TerraRisk Workshop"

    docker-compose -f $COMPOSE_FILE ps

    echo -e "\n${BLUE}Uso de recursos:${NC}"
    docker stats --no-stream terrarisk-api terrarisk-frontend 2>/dev/null || true
}

# Health check
health() {
    print_header "Health Check"

    print_info "Verificando Backend API..."
    if curl -sf http://localhost:8002/api/health > /dev/null; then
        print_success "Backend API: Healthy"
        curl http://localhost:8002/api/health | jq '.'
    else
        print_error "Backend API: No responde"
    fi

    echo ""

    print_info "Verificando Frontend..."
    if curl -sf http://localhost:4001 > /dev/null; then
        print_success "Frontend: Responde correctamente"
    else
        print_error "Frontend: No responde"
    fi

    echo ""

    print_info "Verificando HTTPS público..."
    if curl -sf https://terrarisk.arlexperalta.com > /dev/null; then
        print_success "HTTPS: Accesible públicamente"
    else
        print_warning "HTTPS: No accesible (verificar Nginx Proxy Manager y DNS)"
    fi
}

# Update code and restart
update() {
    print_header "Actualizar Código desde GitHub"

    print_info "Guardando cambios locales (si hay)..."
    git stash

    print_info "Descargando últimos cambios..."
    git pull origin workshop-ui-fixes

    print_info "Restaurando cambios locales..."
    git stash pop 2>/dev/null || true

    print_success "Código actualizado"

    restart
}

# Show usage
usage() {
    echo -e "${BLUE}TerraRisk Workshop - Deploy Script${NC}"
    echo ""
    echo "Usage: $0 [comando]"
    echo ""
    echo "Comandos:"
    echo "  start         - Iniciar servicios"
    echo "  stop          - Detener servicios"
    echo "  restart       - Reiniciar servicios"
    echo "  rebuild       - Rebuild completo (sin caché)"
    echo "  logs [servicio] - Ver logs (api|frontend)"
    echo "  status        - Ver estado de servicios"
    echo "  health        - Health check completo"
    echo "  update        - Actualizar código y reiniciar"
    echo ""
    echo "Ejemplos:"
    echo "  $0 start"
    echo "  $0 logs api"
    echo "  $0 logs frontend"
}

# Main
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    rebuild)
        rebuild
        ;;
    logs)
        logs "$@"
        ;;
    status)
        status
        ;;
    health)
        health
        ;;
    update)
        update
        ;;
    *)
        usage
        exit 1
        ;;
esac
