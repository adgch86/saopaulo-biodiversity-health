#!/bin/bash
# TerraRisk Workshop - Post-Deploy Verification Script
# Ejecutar después del deploy para verificar que todo funciona correctamente

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="terrarisk.arlexperalta.com"
FRONTEND_PORT=4001
BACKEND_PORT=8002

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC} $1\n"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC} $1\n"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC} $1\n"
}

print_info() {
    echo -e "${BLUE}ℹ INFO${NC} $1"
}

# Tests
test_docker_containers() {
    print_header "1. Docker Containers"

    print_test "Verificando contenedor Frontend"
    if docker ps | grep -q "terrarisk-frontend"; then
        print_pass "Contenedor Frontend está corriendo"
    else
        print_fail "Contenedor Frontend NO está corriendo"
        return
    fi

    print_test "Verificando contenedor Backend"
    if docker ps | grep -q "terrarisk-api"; then
        print_pass "Contenedor Backend está corriendo"
    else
        print_fail "Contenedor Backend NO está corriendo"
        return
    fi

    print_test "Verificando healthcheck del Backend"
    if docker inspect terrarisk-api | grep -q '"Status": "healthy"'; then
        print_pass "Backend healthcheck PASS"
    else
        print_warning "Backend healthcheck no está healthy (puede tardar hasta 40s)"
    fi
}

test_local_endpoints() {
    print_header "2. Endpoints Locales"

    print_test "Backend API Health (localhost:$BACKEND_PORT/api/health)"
    if curl -sf http://localhost:$BACKEND_PORT/api/health > /dev/null; then
        RESPONSE=$(curl -s http://localhost:$BACKEND_PORT/api/health)
        if echo "$RESPONSE" | grep -q "healthy"; then
            print_pass "Backend API responde correctamente: $RESPONSE"
        else
            print_fail "Backend API responde pero con formato incorrecto: $RESPONSE"
        fi
    else
        print_fail "Backend API no responde en localhost:$BACKEND_PORT"
    fi

    print_test "Frontend (localhost:$FRONTEND_PORT)"
    if curl -sf http://localhost:$FRONTEND_PORT > /dev/null; then
        print_pass "Frontend responde en localhost:$FRONTEND_PORT"
    else
        print_fail "Frontend no responde en localhost:$FRONTEND_PORT"
    fi
}

test_public_https() {
    print_header "3. HTTPS Público"

    print_test "DNS Propagation ($DOMAIN)"
    DNS_IP=$(dig +short $DOMAIN | head -n1)
    if [ -z "$DNS_IP" ]; then
        print_fail "DNS no resuelve para $DOMAIN (verificar configuración DNS)"
        return
    else
        print_pass "DNS resuelve: $DOMAIN → $DNS_IP"
    fi

    print_test "HTTPS Accesible (https://$DOMAIN)"
    if curl -sf https://$DOMAIN > /dev/null; then
        print_pass "HTTPS responde correctamente"
    else
        print_fail "HTTPS no accesible (verificar Nginx Proxy Manager y SSL)"
        return
    fi

    print_test "Certificado SSL Válido"
    SSL_EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep "notAfter")
    if [ -n "$SSL_EXPIRY" ]; then
        print_pass "Certificado SSL válido: $SSL_EXPIRY"
    else
        print_fail "No se pudo verificar certificado SSL"
    fi

    print_test "HTTP Redirect a HTTPS"
    if curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN | grep -q "301\|302"; then
        print_pass "HTTP redirige correctamente a HTTPS"
    else
        print_warning "HTTP no redirige a HTTPS (verificar Force SSL en NPM)"
    fi
}

test_api_endpoints() {
    print_header "4. API Endpoints"

    print_test "GET /api/health"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/health)
    if [ "$STATUS" = "200" ]; then
        print_pass "Health endpoint responde 200 OK"
    else
        print_fail "Health endpoint responde $STATUS (esperado: 200)"
    fi

    print_test "GET /api/municipalities"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/municipalities)
    if [ "$STATUS" = "200" ]; then
        print_pass "Municipalities endpoint responde 200 OK"
    else
        print_fail "Municipalities endpoint responde $STATUS (esperado: 200)"
    fi

    print_test "GET /api/groups"
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN/api/groups)
    if [ "$STATUS" = "200" ]; then
        print_pass "Groups endpoint responde 200 OK"
    else
        print_fail "Groups endpoint responde $STATUS (esperado: 200)"
    fi
}

test_frontend_pages() {
    print_header "5. Frontend Pages"

    print_test "Homepage (https://$DOMAIN)"
    if curl -sf https://$DOMAIN | grep -q "TerraRisk"; then
        print_pass "Homepage carga correctamente"
    else
        print_warning "Homepage carga pero no contiene 'TerraRisk' (verificar manualmente)"
    fi

    print_test "JavaScript assets"
    if curl -sf https://$DOMAIN | grep -q "_next/static"; then
        print_pass "Next.js assets se están cargando"
    else
        print_fail "Next.js assets no detectados"
    fi
}

test_docker_network() {
    print_header "6. Docker Networking"

    print_test "Red terrarisk-network existe"
    if docker network ls | grep -q "terrarisk-network"; then
        print_pass "Red Docker configurada correctamente"
    else
        print_fail "Red terrarisk-network no existe"
        return
    fi

    print_test "Contenedores en la misma red"
    FRONTEND_NET=$(docker inspect terrarisk-frontend --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')
    BACKEND_NET=$(docker inspect terrarisk-api --format='{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')
    if [ "$FRONTEND_NET" = "$BACKEND_NET" ]; then
        print_pass "Frontend y Backend en la misma red Docker"
    else
        print_fail "Frontend y Backend en redes diferentes (revisar docker-compose.yml)"
    fi
}

test_volumes() {
    print_header "7. Volúmenes de Datos"

    print_test "Volumen de datos del Backend"
    if docker inspect terrarisk-api | grep -q "/app/data"; then
        print_pass "Volumen de datos montado correctamente"
    else
        print_fail "Volumen de datos no montado (mapas no persistirán)"
    fi

    print_test "Directorio de mapas existe"
    if docker exec terrarisk-api ls /app/data/maps/bivariate > /dev/null 2>&1; then
        print_pass "Directorio de mapas bivariados existe"
    else
        print_warning "Directorio de mapas no existe aún (se creará al generar primer mapa)"
    fi
}

test_logs() {
    print_header "8. Logs"

    print_test "Logs del Frontend"
    FRONTEND_LOGS=$(docker logs --tail=50 terrarisk-frontend 2>&1)
    if echo "$FRONTEND_LOGS" | grep -qi "error"; then
        print_warning "Frontend tiene errores en logs (revisar manualmente)"
        echo "$FRONTEND_LOGS" | grep -i "error" | head -n 3
    else
        print_pass "Logs del Frontend sin errores críticos"
    fi

    print_test "Logs del Backend"
    BACKEND_LOGS=$(docker logs --tail=50 terrarisk-api 2>&1)
    if echo "$BACKEND_LOGS" | grep -qi "error\|critical\|exception"; then
        print_warning "Backend tiene errores en logs (revisar manualmente)"
        echo "$BACKEND_LOGS" | grep -iE "error|critical|exception" | head -n 3
    else
        print_pass "Logs del Backend sin errores críticos"
    fi
}

test_performance() {
    print_header "9. Performance"

    print_test "Tiempo de respuesta Frontend"
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' https://$DOMAIN)
    RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d'.' -f1)
    if [ "$RESPONSE_MS" -lt 3000 ]; then
        print_pass "Tiempo de respuesta: ${RESPONSE_MS}ms (< 3s)"
    else
        print_warning "Tiempo de respuesta: ${RESPONSE_MS}ms (verificar performance)"
    fi

    print_test "Tiempo de respuesta API"
    API_RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' https://$DOMAIN/api/health)
    API_RESPONSE_MS=$(echo "$API_RESPONSE_TIME * 1000" | bc | cut -d'.' -f1)
    if [ "$API_RESPONSE_MS" -lt 1000 ]; then
        print_pass "Tiempo de respuesta API: ${API_RESPONSE_MS}ms (< 1s)"
    else
        print_warning "Tiempo de respuesta API: ${API_RESPONSE_MS}ms (verificar performance)"
    fi
}

# Summary
print_summary() {
    print_header "Resumen de Verificación"

    echo -e "Total de pruebas: ${BLUE}$TESTS_TOTAL${NC}"
    echo -e "Pasadas: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Fallidas: ${RED}$TESTS_FAILED${NC}"
    echo ""

    if [ "$TESTS_FAILED" -eq 0 ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✓ DEPLOY EXITOSO${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "La aplicación está funcionando correctamente."
        echo ""
        echo "URLs de acceso:"
        echo "  - Frontend: https://$DOMAIN"
        echo "  - API Health: https://$DOMAIN/api/health"
        echo "  - Nginx Proxy Manager: http://$(hostname -I | awk '{print $1}'):81"
        echo ""
    else
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}✗ HAY PROBLEMAS EN EL DEPLOY${NC}"
        echo -e "${RED}========================================${NC}"
        echo ""
        echo "Revisar logs:"
        echo "  docker-compose -f docker-compose.prod.yml logs -f"
        echo ""
        echo "Ver guías de troubleshooting:"
        echo "  - DEPLOY.md"
        echo "  - NGINX-PROXY-MANAGER-SETUP.md"
        echo ""
    fi
}

# Main execution
main() {
    print_header "TerraRisk Workshop - Verificación Post-Deploy"
    print_info "Verificando deployment en $DOMAIN\n"

    test_docker_containers
    test_local_endpoints
    test_public_https
    test_api_endpoints
    test_frontend_pages
    test_docker_network
    test_volumes
    test_logs
    test_performance

    print_summary
}

# Run
main
