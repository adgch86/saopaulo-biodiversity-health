# Pre-Deploy Checklist - TerraRisk Workshop

Verificar ANTES de hacer deploy al VPS Contabo.

---

## 1. Archivos de Configuración

- [ ] `docker-compose.prod.yml` existe y está configurado
- [ ] `.env.production` existe con variables correctas
- [ ] `deploy.sh` existe y es ejecutable (`chmod +x`)
- [ ] `.dockerignore` existe en raíz, backend y frontend

---

## 2. Docker (Local)

### Build Local

```bash
# Desde la raíz del proyecto
docker-compose -f docker-compose.prod.yml build
```

- [ ] Build del backend completo sin errores
- [ ] Build del frontend completo sin errores
- [ ] Imágenes creadas: `terrarisk-workshop-api` y `terrarisk-workshop-frontend`

### Test Local

```bash
docker-compose -f docker-compose.prod.yml up
```

- [ ] Backend inicia sin errores
- [ ] Frontend inicia sin errores
- [ ] Backend health check pasa: `curl http://localhost:8002/api/health`
- [ ] Frontend responde: `curl http://localhost:4001`
- [ ] Logs sin errores críticos

**Si TODO funciona localmente, detener:**

```bash
docker-compose -f docker-compose.prod.yml down
```

---

## 3. Código

- [ ] Último commit pusheado a GitHub
- [ ] Branch `workshop-ui-fixes` actualizado
- [ ] No hay cambios sin commitear críticos
- [ ] Tests pasan (si hay)

---

## 4. Servidor VPS (Pre-requisitos)

### Conectar

```bash
ssh contabo
```

### Verificar Docker

```bash
docker --version
docker-compose --version
```

- [ ] Docker instalado (v20+)
- [ ] Docker Compose instalado (v2+)

### Verificar Nginx Proxy Manager

```bash
docker ps | grep nginx-proxy-manager
```

- [ ] NPM corriendo
- [ ] Accesible en http://161.97.95.132:81

### Verificar Puertos Libres

```bash
sudo lsof -i :4001
sudo lsof -i :8002
```

- [ ] Puerto 4001 libre (o detenido proyecto anterior)
- [ ] Puerto 8002 libre (o detenido proyecto anterior)

---

## 5. DNS

### Verificar Propagación

```bash
nslookup terrarisk.arlexperalta.com
```

- [ ] Resuelve a 161.97.95.132
- [ ] Sin errores de DNS

**Si no está propagado:**
- Esperar 5-60 minutos después de configurar DNS
- O continuar y configurar SSL después

---

## 6. Firewall

```bash
sudo ufw status
```

- [ ] Puerto 80 abierto (para Let's Encrypt)
- [ ] Puerto 443 abierto (HTTPS)
- [ ] Puerto 4001 abierto (opcional, acceso directo)
- [ ] Puerto 8002 abierto (opcional, API directa)

**Si están bloqueados:**

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 4001/tcp
sudo ufw allow 8002/tcp
sudo ufw reload
```

---

## 7. Espacio en Disco

```bash
df -h /opt
```

- [ ] Al menos 2GB libres en `/opt`
- [ ] Al menos 1GB libres en `/var/lib/docker`

**Limpiar si es necesario:**

```bash
# Limpiar contenedores detenidos
docker container prune -f

# Limpiar imágenes sin usar
docker image prune -a -f

# Limpiar volúmenes huérfanos
docker volume prune -f
```

---

## 8. Backup (Opcional pero Recomendado)

Si ya hay una versión anterior corriendo:

```bash
# Backup de datos de mapas
cd /opt/terrarisk-workshop
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz backend/data/

# Mover a carpeta de backups
sudo mkdir -p /opt/backups/terrarisk
sudo mv backup-*.tar.gz /opt/backups/terrarisk/
```

- [ ] Backup creado (si aplica)

---

## 9. Variables de Entorno

Verificar que `.env.production` tenga:

```bash
cat .env.production
```

- [ ] `NEXT_PUBLIC_API_URL=http://api:8000`
- [ ] `NODE_ENV=production`
- [ ] `PYTHONUNBUFFERED=1`
- [ ] Sin secrets expuestos (API keys, passwords)

---

## 10. GitHub Access

```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

- [ ] Servidor puede clonar de GitHub sin password
- [ ] SSH key configurado (o usar HTTPS)

---

## Resultado del Checklist

**Todos los items marcados = LISTO PARA DEPLOY**

Proceder con: `./deploy.sh start`

**Si falta algún item:**
- No hacer deploy aún
- Resolver el problema primero
- Re-verificar checklist

---

## Troubleshooting Rápido

### Docker no está instalado

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

### Docker Compose no está instalado

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### Nginx Proxy Manager no está corriendo

```bash
cd /opt/nginx-proxy-manager  # o donde esté instalado
docker-compose up -d
```

### DNS no propaga

- Verificar configuración en panel DNS (Cloudflare, OVH, etc.)
- Esperar hasta 1 hora para propagación completa
- Continuar deploy, configurar SSL después

---

## Siguiente Paso

Una vez que TODO esté marcado:

**[Ver QUICK-START.md](QUICK-START.md)** para ejecutar el deploy en 5 minutos.
