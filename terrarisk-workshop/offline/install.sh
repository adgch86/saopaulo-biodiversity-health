#!/bin/bash
echo "============================================"
echo "  TerraRisk Workshop - Instalacion Offline"
echo "============================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker no esta instalado."
    echo "Descarga Docker Desktop: https://www.docker.com/products/docker-desktop/"
    echo "Instala, reinicia y vuelve a correr este script."
    exit 1
fi

# Check Docker running
if ! docker info &> /dev/null; then
    echo "[ERROR] Docker no esta corriendo. Abre Docker Desktop y espera a que inicie."
    exit 1
fi

echo "[OK] Docker detectado"
echo ""

# Load images
echo "Cargando imagenes Docker (puede tardar 2-3 minutos)..."
echo ""

if [ -f "images/terrarisk-api.tar" ]; then
    echo "  Cargando API..."
    docker load -i images/terrarisk-api.tar
    echo "  [OK] API cargada"
else
    echo "  [ERROR] No se encontro images/terrarisk-api.tar"
    exit 1
fi

if [ -f "images/terrarisk-frontend.tar" ]; then
    echo "  Cargando Frontend..."
    docker load -i images/terrarisk-frontend.tar
    echo "  [OK] Frontend cargado"
else
    echo "  [ERROR] No se encontro images/terrarisk-frontend.tar"
    exit 1
fi

if [ -f "images/nginx-alpine.tar" ]; then
    echo "  Cargando Tile Server..."
    docker load -i images/nginx-alpine.tar
    echo "  [OK] Tile Server cargado"
else
    echo "  [ERROR] No se encontro images/nginx-alpine.tar"
    exit 1
fi

echo ""
echo "Iniciando TerraRisk..."
docker compose -f docker-compose.offline.yml up -d

echo ""
echo "============================================"
echo "  TerraRisk esta corriendo!"
echo ""
echo "  Abre en el navegador:"
echo "  http://localhost:4001"
echo ""
echo "  Para detener: docker compose -f docker-compose.offline.yml down"
echo "============================================"
