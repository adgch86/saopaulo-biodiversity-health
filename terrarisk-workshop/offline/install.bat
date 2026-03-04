@echo off
echo ============================================
echo   TerraRisk Workshop - Instalacion Offline
echo ============================================
echo.

:: Check Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta instalado.
    echo Descarga Docker Desktop: https://www.docker.com/products/docker-desktop/
    echo Instala, reinicia y vuelve a correr este script.
    pause
    exit /b 1
)

:: Check Docker running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta corriendo. Abre Docker Desktop y espera a que inicie.
    pause
    exit /b 1
)

echo [OK] Docker detectado
echo.

:: Load images
echo Cargando imagenes Docker (puede tardar 2-3 minutos)...
echo.

if exist images\terrarisk-api.tar (
    echo   Cargando API...
    docker load -i images\terrarisk-api.tar
    echo   [OK] API cargada
) else (
    echo   [ERROR] No se encontro images\terrarisk-api.tar
    pause
    exit /b 1
)

if exist images\terrarisk-frontend.tar (
    echo   Cargando Frontend...
    docker load -i images\terrarisk-frontend.tar
    echo   [OK] Frontend cargado
) else (
    echo   [ERROR] No se encontro images\terrarisk-frontend.tar
    pause
    exit /b 1
)

if exist images\nginx-alpine.tar (
    echo   Cargando Tile Server...
    docker load -i images\nginx-alpine.tar
    echo   [OK] Tile Server cargado
) else (
    echo   [ERROR] No se encontro images\nginx-alpine.tar
    pause
    exit /b 1
)

echo.
echo Iniciando TerraRisk...
docker compose -f docker-compose.offline.yml up -d

echo.
echo ============================================
echo   TerraRisk esta corriendo!
echo.
echo   Abre en el navegador:
echo   http://localhost:4001
echo.
echo   Para detener: docker compose -f docker-compose.offline.yml down
echo ============================================
echo.
pause
