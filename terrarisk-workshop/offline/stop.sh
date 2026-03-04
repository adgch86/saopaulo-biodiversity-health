#!/bin/bash
echo "Deteniendo TerraRisk..."
docker compose -f docker-compose.offline.yml down
echo "TerraRisk detenido."
