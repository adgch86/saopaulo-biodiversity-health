# TerraRisk Workshop - Documentación de Infraestructura

## Overview

Aplicación web de workshop científico para generación colaborativa de mapas bivariados de biodiversidad y salud en São Paulo, Brasil.

**Stack:** Next.js 14 (frontend) + FastAPI (backend) + Docker + Nginx Proxy Manager

---

## Arquitectura de Producción

```
Internet
   |
   v
[DNS: terrarisk.arlexperalta.com] → 161.97.95.132
   |
   v
[Nginx Proxy Manager] (Puerto 80/443)
   |-- SSL (Let's Encrypt)
   |-- Proxy reverso
   v
[Docker Network: terrarisk-network]
   |
   |-- [Frontend Container]
   |     |-- Next.js 14 standalone
   |     |-- Puerto interno: 3000
   |     |-- Puerto expuesto: 4001
   |     |-- Imagen: terrarisk-workshop-frontend
   |
   |-- [Backend Container]
         |-- FastAPI + Uvicorn
         |-- Puerto interno: 8000
         |-- Puerto expuesto: 8002
         |-- Imagen: terrarisk-workshop-api
         |-- Volumen: ./backend/data → /app/data
```

---

## Servidor

### Contabo VPS

| Atributo | Valor |
|----------|-------|
| IP Pública | 161.97.95.132 |
| OS | Ubuntu 22.04 LTS |
| SSH | `ssh contabo` |
| Docker | v24.0+ |
| Docker Compose | v2.20+ |
| Firewall | UFW (80, 443, 4001, 8002) |

---

## Dominios y SSL

| Dominio | Tipo | Apunta a | SSL |
|---------|------|----------|-----|
| terrarisk.arlexperalta.com | A | 161.97.95.132 | Let's Encrypt (auto) |

**Gestión SSL:** Nginx Proxy Manager (renovación automática 30 días antes de expirar)

---

## Contenedores Docker

### Frontend (Next.js)

```yaml
Container: terrarisk-frontend
Image: terrarisk-workshop-frontend
Build: ./frontend/Dockerfile
Port Mapping: 4001:3000
Environment:
  - NEXT_PUBLIC_API_URL=http://api:8000
  - NODE_ENV=production
Restart: unless-stopped
Network: terrarisk-network
```

**Dockerfile:**
- Multi-stage build (deps → builder → runner)
- Output: standalone (optimizado para Docker)
- User: nextjs (non-root)
- Base: node:20-alpine

### Backend (FastAPI)

```yaml
Container: terrarisk-api
Image: terrarisk-workshop-api
Build: ./backend/Dockerfile
Port Mapping: 8002:8000
Environment:
  - PYTHONUNBUFFERED=1
  - ENVIRONMENT=production
Volume: ./backend/data:/app/data
Healthcheck: curl http://localhost:8000/api/health (30s)
Restart: unless-stopped
Network: terrarisk-network
```

**Dockerfile:**
- Base: python:3.11-slim
- Dependencies: GDAL, geopandas, matplotlib
- User: root (necesario para GDAL)
- CMD: uvicorn main:app --host 0.0.0.0 --port 8000

---

## Networking

### Docker Bridge Network

```yaml
Name: terrarisk-network
Driver: bridge
Containers:
  - terrarisk-frontend
  - terrarisk-api
```

**Comunicación interna:**
- Frontend → Backend: `http://api:8000` (DNS interno Docker)
- Backend responde en todas las interfaces: `0.0.0.0:8000`

**Comunicación externa:**
- Frontend: `http://161.97.95.132:4001` o `https://terrarisk.arlexperalta.com`
- Backend: `http://161.97.95.132:8002` (directo, no expuesto públicamente via NPM)

---

## Nginx Proxy Manager

### Configuración

```yaml
UI: http://161.97.95.132:81
Proxy Host:
  Domain: terrarisk.arlexperalta.com
  Scheme: http
  Forward to: 172.17.0.1:4001
  SSL: Let's Encrypt (auto)
  Force SSL: Yes
  HTTP/2: Yes
  HSTS: Yes
  Websockets: Yes
```

**Gateway IP:**
- `172.17.0.1` = IP del host Docker (bridge network)
- Alternativa: IP privada del VPS (consultar con `ip addr`)

---

## Almacenamiento de Datos

### Volúmenes Docker

```yaml
Volume: ./backend/data
Mount: /app/data
Contenido:
  - /maps/bivariate/*.png (mapas generados)
  - Logs del backend
Backup: Recomendado diario (tar.gz)
```

**Persistencia:**
- Mapas generados se guardan en el host
- Sobreviven a `docker-compose down`
- **CRÍTICO:** Hacer backup antes de `docker-compose down -v`

---

## Variables de Entorno

### Archivo: `.env.production`

```env
# Backend
PYTHONUNBUFFERED=1
ENVIRONMENT=production

# Frontend
NEXT_PUBLIC_API_URL=http://api:8000
NODE_ENV=production
```

**Nota:**
- `NEXT_PUBLIC_API_URL` es **interna** (container-to-container)
- El frontend usa rewrites de Next.js para proxy de `/api/*` al backend

---

## Puertos

| Puerto | Servicio | Acceso |
|--------|----------|--------|
| 80 | Nginx Proxy Manager (HTTP) | Público (redirige a 443) |
| 443 | Nginx Proxy Manager (HTTPS) | Público |
| 81 | Nginx Proxy Manager (UI) | Privado (admin) |
| 3000 | Frontend (interno) | Solo Docker network |
| 4001 | Frontend (expuesto) | Host local + Público |
| 8000 | Backend (interno) | Solo Docker network |
| 8002 | Backend (expuesto) | Host local (no proxy NPM) |

---

## Logs

### Configuración de Logging

```yaml
Driver: json-file
Max Size: 10MB
Max Files: 3
Total per container: ~30MB
```

### Comandos de Logs

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs del backend
docker logs -f terrarisk-api

# Logs del frontend
docker logs -f terrarisk-frontend

# Últimas 100 líneas
docker logs --tail=100 terrarisk-api
```

---

## Healthchecks

### Backend

```yaml
Test: curl -f http://localhost:8000/api/health
Interval: 30s
Timeout: 10s
Retries: 3
Start Period: 40s
```

**Respuesta esperada:**
```json
{"status": "healthy", "version": "1.0.0"}
```

### Frontend

No tiene healthcheck configurado (Next.js standalone es resiliente).

**Verificar manualmente:**
```bash
curl -I http://localhost:4001
# HTTP/1.1 200 OK
```

---

## Seguridad

### SSL/TLS

- **Certificado:** Let's Encrypt (RSA 2048)
- **Renovación:** Automática (30 días antes de expirar)
- **Protocolos:** TLSv1.2, TLSv1.3
- **Ciphers:** Mozilla Modern profile
- **HSTS:** Habilitado (max-age 31536000)

### CORS

```python
# backend/main.py
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

**Nota:** En producción, considerar restringir `allow_origins` a dominio específico.

### Firewall (UFW)

```bash
sudo ufw status
```

| Puerto | Estado | Razón |
|--------|--------|-------|
| 22 | ALLOW | SSH |
| 80 | ALLOW | HTTP (Let's Encrypt challenge) |
| 443 | ALLOW | HTTPS |
| 4001 | ALLOW | Frontend directo (opcional) |
| 8002 | ALLOW | Backend directo (opcional) |

---

## Performance

### Recursos por Contenedor

| Container | CPU | RAM | Disk |
|-----------|-----|-----|------|
| Frontend | ~5% | ~200MB | ~500MB |
| Backend | ~10% | ~300MB | ~1GB |
| **Total** | ~15% | ~500MB | ~1.5GB |

**VPS Contabo tiene recursos suficientes para:**
- 20+ grupos simultáneos en workshop
- Generación de 100+ mapas bivariados sin degradación

### Optimizaciones

- **Frontend:** Next.js standalone (50% más ligero que full build)
- **Backend:** Uvicorn con workers=1 (suficiente para workshop)
- **Imágenes Docker:** Multi-stage builds, alpine base
- **Cache:** Nginx Proxy Manager cachea assets estáticos

---

## Backup Strategy

### Qué respaldar

```bash
/opt/terrarisk-workshop/backend/data/
```

**Contiene:**
- Mapas bivariados generados (`.png`)
- Configuración de grupos (si se persiste en JSON/SQLite)

### Script de Backup (recomendado)

```bash
#!/bin/bash
# backup-terrarisk.sh

BACKUP_DIR="/opt/backups/terrarisk"
SOURCE_DIR="/opt/terrarisk-workshop/backend/data"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/terrarisk-data-$DATE.tar.gz $SOURCE_DIR

# Mantener solo últimos 7 días
find $BACKUP_DIR -name "terrarisk-data-*.tar.gz" -mtime +7 -delete

echo "Backup completado: terrarisk-data-$DATE.tar.gz"
```

**Cron job (diario a las 3 AM):**

```bash
crontab -e
# Agregar:
0 3 * * * /opt/terrarisk-workshop/backup-terrarisk.sh
```

---

## Monitoreo (Opcional)

### Uptime Monitoring

Servicios recomendados:
- UptimeRobot (free, 5 min intervals)
- Pingdom
- Better Uptime

**URL a monitorear:**
```
https://terrarisk.arlexperalta.com/api/health
```

### Alertas

Configurar notificación si:
- Response time > 5s
- HTTP status != 200
- SSL expira en < 7 días

---

## Disaster Recovery

### Escenario 1: Contenedor crashea

```bash
./deploy.sh restart
```

### Escenario 2: Servidor se reinicia

Los contenedores arrancan automáticamente (`restart: unless-stopped`).

Verificar:
```bash
docker ps
./deploy.sh status
```

### Escenario 3: Corrupción de datos

Restaurar desde backup:
```bash
cd /opt/terrarisk-workshop
docker-compose -f docker-compose.prod.yml down
rm -rf backend/data/*
tar -xzf /opt/backups/terrarisk/terrarisk-data-YYYYMMDD-HHMMSS.tar.gz -C .
docker-compose -f docker-compose.prod.yml up -d
```

### Escenario 4: Deploy fallido

Rollback a versión anterior:
```bash
git log --oneline  # Ver commits
git checkout <commit-hash-anterior>
./deploy.sh rebuild
```

---

## Costos

| Recurso | Costo Mensual (USD) |
|---------|---------------------|
| Contabo VPS | ~$5-10 (plan básico) |
| Dominio arlexperalta.com | ~$12/año |
| Let's Encrypt SSL | Gratis |
| **Total** | ~$6-11/mes |

---

## Contactos

| Rol | Nombre | Responsabilidad |
|-----|--------|-----------------|
| DevOps | Arlex Peralta | Deploy, infraestructura |
| Product Owner | Dr. Adrian David González | Features, roadmap |
| Reviewer | Monti | QA, testing |

---

## Referencias

- **Repo GitHub:** https://github.com/adgch86/saopaulo-biodiversity-health
- **Branch:** `workshop-ui-fixes`
- **Documentación Deploy:** [DEPLOY.md](DEPLOY.md)
- **Quick Start:** [QUICK-START.md](QUICK-START.md)
- **Nginx Setup:** [NGINX-PROXY-MANAGER-SETUP.md](NGINX-PROXY-MANAGER-SETUP.md)

---

## Changelog de Infraestructura

| Fecha | Cambio | Autor |
|-------|--------|-------|
| 2026-02-10 | Deploy inicial a Contabo VPS | Arlex Peralta |
| 2026-02-10 | Configuración Nginx Proxy Manager | Arlex Peralta |
| 2026-02-10 | SSL Let's Encrypt configurado | Arlex Peralta |

---

**Última actualización:** 2026-02-10
**Versión de este documento:** 1.0.0
