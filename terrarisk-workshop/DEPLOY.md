# Deploy TerraRisk Workshop - Contabo VPS

## Información del Servidor

- **VPS**: Contabo - 161.97.95.132
- **SSH**: `ssh contabo`
- **Dominio**: terrarisk.arlexperalta.com
- **Puertos**:
  - Frontend: 4001 (interno 3000)
  - Backend API: 8002 (interno 8000)

---

## Pre-requisitos

### En el servidor deben estar instalados:

```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker-compose --version

# Verificar Nginx Proxy Manager corriendo
docker ps | grep nginx-proxy-manager
```

Si falta algo:

```bash
# Instalar Docker (si no está)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose (si no está)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

---

## Paso 1: Conectar al Servidor

```bash
ssh contabo
```

---

## Paso 2: Clonar o Actualizar el Repositorio

### Si es la primera vez (clonar):

```bash
cd /opt
sudo mkdir -p terrarisk-workshop
sudo chown $USER:$USER terrarisk-workshop
cd terrarisk-workshop

git clone https://github.com/adgch86/saopaulo-biodiversity-health.git .
git checkout workshop-ui-fixes
```

### Si ya existe (actualizar):

```bash
cd /opt/terrarisk-workshop

# Guardar cambios locales si los hay
git stash

# Actualizar código
git pull origin workshop-ui-fixes

# Restaurar cambios locales (si aplica)
git stash pop
```

---

## Paso 3: Verificar Archivos de Configuración

```bash
# Verificar que existan los archivos necesarios
ls -la docker-compose.prod.yml
ls -la .env.production
ls -la backend/Dockerfile
ls -la frontend/Dockerfile

# Copiar .env.production si no existe
cp .env.production .env
```

---

## Paso 4: Build de las Imágenes Docker

```bash
# Build de ambos servicios (puede tardar 5-10 minutos)
docker-compose -f docker-compose.prod.yml build --no-cache

# Ver imágenes creadas
docker images | grep terrarisk
```

---

## Paso 5: Levantar los Servicios

```bash
# Levantar servicios en background
docker-compose -f docker-compose.prod.yml up -d

# Ver logs en tiempo real
docker-compose -f docker-compose.prod.yml logs -f

# Verificar que están corriendo
docker-compose -f docker-compose.prod.yml ps
```

**Salida esperada:**

```
NAME                    IMAGE                        STATUS         PORTS
terrarisk-api           terrarisk-workshop-api       Up (healthy)   0.0.0.0:8002->8000/tcp
terrarisk-frontend      terrarisk-workshop-frontend  Up             0.0.0.0:4001->3000/tcp
```

---

## Paso 6: Verificar Health del Backend

```bash
# Probar endpoint de salud
curl http://localhost:8002/api/health

# Respuesta esperada:
# {"status":"healthy","version":"1.0.0"}
```

---

## Paso 7: Verificar Frontend

```bash
# Probar que el frontend responda
curl -I http://localhost:4001

# Respuesta esperada: HTTP/1.1 200 OK
```

---

## Paso 8: Configurar Nginx Proxy Manager

### A. Acceder a Nginx Proxy Manager

Abrir en navegador:
```
http://161.97.95.132:81
```

**Credenciales por defecto:**
- Email: admin@example.com
- Password: changeme

(Si es la primera vez, cambiar password inmediatamente)

### B. Crear Proxy Host

1. Click en **"Proxy Hosts"** → **"Add Proxy Host"**

2. Pestaña **"Details"**:
   - **Domain Names**: `terrarisk.arlexperalta.com`
   - **Scheme**: `http`
   - **Forward Hostname / IP**: `172.17.0.1` (IP del host Docker)
   - **Forward Port**: `4001`
   - **Cache Assets**: ✓ (opcional)
   - **Block Common Exploits**: ✓
   - **Websockets Support**: ✓

3. Pestaña **"SSL"**:
   - **SSL Certificate**: Dropdown → **"Request a new SSL Certificate"**
   - **Force SSL**: ✓
   - **HTTP/2 Support**: ✓
   - **HSTS Enabled**: ✓
   - **Email Address for Let's Encrypt**: `tu-email@ejemplo.com`
   - **I Agree to Let's Encrypt ToS**: ✓

4. Click **"Save"**

**Resultado esperado:**
- SSL se genera automáticamente en 1-2 minutos
- El proxy host aparece en la lista con estado "Online"

### C. Verificar Configuración

```bash
# Ver logs de Nginx Proxy Manager
docker logs -f nginx-proxy-manager
```

---

## Paso 9: Configurar DNS (Si no está configurado)

En tu panel de DNS (Cloudflare, OVH, etc.):

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | terrarisk | 161.97.95.132 | Auto |

**Propagación DNS:** 5-60 minutos (verificar con `nslookup terrarisk.arlexperalta.com`)

---

## Paso 10: Verificar Deploy Completo

```bash
# Test HTTPS público
curl -I https://terrarisk.arlexperalta.com

# Respuesta esperada: HTTP/2 200
```

**Abrir en navegador:**
```
https://terrarisk.arlexperalta.com
```

**Deberías ver:**
- La app TerraRisk Workshop cargando
- Certificado SSL válido (candado verde)
- API funcionando (probar un municipio en el mapa)

---

## Comandos Útiles de Mantenimiento

### Ver logs

```bash
# Logs de todos los servicios
docker-compose -f docker-compose.prod.yml logs -f

# Logs solo del backend
docker-compose -f docker-compose.prod.yml logs -f api

# Logs solo del frontend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Últimas 100 líneas
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### Reiniciar servicios

```bash
# Reiniciar todo
docker-compose -f docker-compose.prod.yml restart

# Reiniciar solo backend
docker-compose -f docker-compose.prod.yml restart api

# Reiniciar solo frontend
docker-compose -f docker-compose.prod.yml restart frontend
```

### Detener servicios

```bash
# Detener sin borrar contenedores
docker-compose -f docker-compose.prod.yml stop

# Detener y borrar contenedores (mantiene volúmenes)
docker-compose -f docker-compose.prod.yml down

# Detener y borrar TODO (incluyendo volúmenes de datos)
docker-compose -f docker-compose.prod.yml down -v
```

### Actualizar código sin rebuild

```bash
cd /opt/terrarisk-workshop
git pull origin workshop-ui-fixes
docker-compose -f docker-compose.prod.yml restart
```

### Rebuild completo (después de cambios en Dockerfile o dependencias)

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Ver estado de contenedores

```bash
# Estado
docker-compose -f docker-compose.prod.yml ps

# Uso de recursos
docker stats terrarisk-api terrarisk-frontend

# Entrar a un contenedor
docker exec -it terrarisk-api bash
docker exec -it terrarisk-frontend sh
```

### Ver volúmenes de datos

```bash
# Listar volúmenes
docker volume ls | grep terrarisk

# Ver contenido del volumen de datos del backend
docker exec -it terrarisk-api ls -la /app/data/maps/bivariate
```

---

## Troubleshooting

### Problema: Frontend no conecta con Backend

```bash
# Verificar que ambos estén en la misma red
docker network inspect terrarisk-network

# Probar conectividad desde frontend a backend
docker exec -it terrarisk-frontend wget -O- http://api:8000/api/health
```

### Problema: Backend no inicia (healthcheck falla)

```bash
# Ver logs detallados
docker-compose -f docker-compose.prod.yml logs api

# Verificar dependencias Python instaladas
docker exec -it terrarisk-api pip list

# Probar endpoint manualmente
docker exec -it terrarisk-api curl http://localhost:8000/api/health
```

### Problema: SSL no se genera en Nginx Proxy Manager

- Verificar que el puerto 80 y 443 estén abiertos en el firewall del VPS
- Verificar que el DNS apunte correctamente (propagación completa)
- Ver logs: `docker logs nginx-proxy-manager`

### Problema: "Error: Cannot find module 'next'"

El frontend no se buildeó correctamente:

```bash
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

---

## URLs de Verificación

Una vez deployed, verificar:

| URL | Qué debe mostrar |
|-----|------------------|
| https://terrarisk.arlexperalta.com | App principal |
| https://terrarisk.arlexperalta.com/api/health | `{"status":"healthy","version":"1.0.0"}` |
| https://terrarisk.arlexperalta.com/maps/bivariate/ | Listado de mapas PNG generados (si hay) |

---

## Notas para Adrian y Monti

- **Workshop Flow**: La app está diseñada para sesiones de workshop donde cada grupo genera sus mapas bivariados
- **Datos persistentes**: Los mapas generados se guardan en `/opt/terrarisk-workshop/backend/data` del servidor
- **Backup**: Recomendado hacer backup periódico de `/opt/terrarisk-workshop/backend/data`
- **Performance**: El servidor Contabo tiene recursos suficientes para ~20 grupos simultáneos
- **Logs**: Se rotan automáticamente (máx 10MB x 3 archivos)

---

## Contacto de Soporte

- **Arlex Peralta** (DevOps)
- **Dr. Adrian David** (Cliente/Investigador Principal)
- **Monti** (Reviewer)

---

## Checklist Final

- [ ] Servicios Docker corriendo (api + frontend)
- [ ] Backend healthcheck pasa (`/api/health` responde)
- [ ] Frontend accesible vía HTTPS
- [ ] SSL válido (certificado Let's Encrypt)
- [ ] Proxy de Nginx configurado correctamente
- [ ] DNS propagado (`nslookup terrarisk.arlexperalta.com`)
- [ ] Logs sin errores críticos
- [ ] App funcional en navegador
- [ ] API endpoints responden correctamente
- [ ] Mapas bivariados se pueden generar y descargar

**Deploy exitoso cuando todos los items están chequeados.**
