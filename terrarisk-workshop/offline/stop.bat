@echo off
echo Deteniendo TerraRisk...
docker compose -f docker-compose.offline.yml down
echo.
echo TerraRisk detenido.
pause
