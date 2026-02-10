# TerraRisk Workshop - Quick Start

Guía rápida para hacer deploy en el VPS Contabo en 5 minutos.

---

## Para Arlex (DevOps)

### 1. SSH al servidor

```bash
ssh contabo
```

### 2. Clonar repo (primera vez)

```bash
cd /opt
sudo mkdir -p terrarisk-workshop
sudo chown $USER:$USER terrarisk-workshop
cd terrarisk-workshop

git clone https://github.com/adgch86/saopaulo-biodiversity-health.git .
git checkout workshop-ui-fixes
```

### 3. Hacer el script ejecutable

```bash
chmod +x deploy.sh
```

### 4. Deploy automático

```bash
./deploy.sh start
```

**Listo.** El script se encarga de:
- Build de imágenes Docker
- Levantar servicios (frontend + backend)
- Verificar health
- Mostrar URLs de acceso

### 5. Configurar Nginx Proxy Manager

Ir a: http://161.97.95.132:81

**Crear Proxy Host:**
- Domain: `terrarisk.arlexperalta.com`
- Forward to: `172.17.0.1:4001`
- SSL: Request new certificate (Let's Encrypt)

Ver guía completa en `NGINX-PROXY-MANAGER-SETUP.md`

### 6. Verificar deploy

```bash
./deploy.sh health
```

Abrir: https://terrarisk.arlexperalta.com

---

## Para Adrian y Monti (Review)

Una vez que Arlex haga el deploy, acceder a:

**URL de Staging:** https://terrarisk.arlexperalta.com

### Probar:

1. **Home page**
   - ✓ Mapa de São Paulo carga
   - ✓ Lista de municipios en panel izquierdo
   - ✓ Tabs "Municipios" y "Workshop" funcionan

2. **Funcionalidad Workshop**
   - ✓ Crear grupos
   - ✓ Asignar municipios a grupos
   - ✓ Drag & drop funciona
   - ✓ Generar mapas bivariados
   - ✓ Descargar mapas PNG

3. **Performance**
   - ✓ Carga inicial < 3 segundos
   - ✓ Generación de mapas < 10 segundos
   - ✓ Sin errores en consola del navegador

### Reportar bugs

Si encuentran problemas, enviar a Arlex:

1. **URL exacta** donde ocurre el error
2. **Screenshot** del error
3. **Pasos para reproducir**
4. **Navegador y versión** (ej: Chrome 120)

---

## Comandos Útiles (para Arlex)

```bash
# Ver logs en tiempo real
./deploy.sh logs

# Ver logs solo del backend
./deploy.sh logs api

# Ver logs solo del frontend
./deploy.sh logs frontend

# Reiniciar todo
./deploy.sh restart

# Actualizar código desde GitHub
./deploy.sh update

# Rebuild completo (si hay cambios en Dockerfile)
./deploy.sh rebuild

# Ver estado de servicios
./deploy.sh status

# Health check completo
./deploy.sh health
```

---

## URLs de Verificación

| URL | Qué debe mostrar |
|-----|------------------|
| https://terrarisk.arlexperalta.com | App principal |
| https://terrarisk.arlexperalta.com/api/health | `{"status":"healthy"}` |
| http://161.97.95.132:4001 | Frontend directo (bypass Nginx) |
| http://161.97.95.132:8002/api/health | Backend directo |

---

## Credenciales

### Nginx Proxy Manager

- URL: http://161.97.95.132:81
- User: `admin@example.com`
- Pass: `changeme` (cambiar en primer login)

### SSH Contabo

```bash
ssh contabo
# Configurado en ~/.ssh/config de Arlex
```

---

## Estructura de Archivos en Servidor

```
/opt/terrarisk-workshop/
├── backend/
│   ├── data/               # Mapas generados (persistente)
│   ├── Dockerfile
│   └── main.py
├── frontend/
│   ├── Dockerfile
│   └── src/
├── docker-compose.prod.yml  # Config de producción
├── .env.production          # Variables de entorno
├── deploy.sh                # Script de deploy (usar este)
├── DEPLOY.md                # Guía completa
└── NGINX-PROXY-MANAGER-SETUP.md
```

---

## Checklist de Deploy

- [ ] SSH al servidor funciona
- [ ] Repo clonado en `/opt/terrarisk-workshop`
- [ ] `deploy.sh start` ejecutado exitosamente
- [ ] Ambos contenedores corriendo (verificar con `docker ps`)
- [ ] Backend healthy (`/api/health` responde)
- [ ] Nginx Proxy Manager configurado
- [ ] SSL generado (Let's Encrypt)
- [ ] DNS propagado (`nslookup terrarisk.arlexperalta.com`)
- [ ] HTTPS accesible desde navegador
- [ ] App funcional sin errores
- [ ] Notificar a Adrian y Monti

**Deploy completo cuando todos los items están chequeados.**

---

## Próximos Pasos (Post-Deploy)

1. **Monitoreo**: Configurar alertas si el servicio cae
2. **Backup**: Script de backup automático de `/backend/data`
3. **Analytics**: Agregar tracking opcional (Google Analytics)
4. **Documentación**: Crear guía de usuario para workshop
5. **Testing**: Hacer dry-run con 3-5 grupos simultáneos

---

## Contacto

- **Arlex Peralta** - DevOps/Deploy
- **Dr. Adrian David** - Product Owner
- **Monti** - Reviewer

**Repo GitHub:** https://github.com/adgch86/saopaulo-biodiversity-health
**Branch:** `workshop-ui-fixes`
