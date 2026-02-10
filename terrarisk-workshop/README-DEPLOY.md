# TerraRisk Workshop - Deploy to Production

Deploy guide for TerraRisk Workshop staging environment on Contabo VPS.

---

## Quick Links

| Document | Purpose | Audience |
|----------|---------|----------|
| **[QUICK-START.md](QUICK-START.md)** | Deploy en 5 minutos | Arlex (DevOps) |
| **[DEPLOYMENT-SUMMARY.md](DEPLOYMENT-SUMMARY.md)** | Resumen ejecutivo completo | Todos |
| **[DEPLOY.md](DEPLOY.md)** | Guía detallada paso a paso | Arlex (DevOps) |
| **[NGINX-PROXY-MANAGER-SETUP.md](NGINX-PROXY-MANAGER-SETUP.md)** | Configuración SSL y proxy | Arlex (DevOps) |
| **[PRE-DEPLOY-CHECKLIST.md](PRE-DEPLOY-CHECKLIST.md)** | Verificación pre-deploy | Arlex (DevOps) |
| **[INFRASTRUCTURE.md](INFRASTRUCTURE.md)** | Documentación técnica completa | Todos |

---

## For Arlex (DevOps)

### First-Time Deploy (New Server)

1. **Read the checklist first:**
   ```bash
   cat PRE-DEPLOY-CHECKLIST.md
   ```

2. **Follow the quick start:**
   ```bash
   cat QUICK-START.md
   ```

3. **Or follow detailed guide:**
   ```bash
   cat DEPLOY.md
   ```

### Updating Existing Deployment

```bash
ssh contabo
cd /opt/terrarisk-workshop
./deploy.sh update
```

---

## For Adrian and Monti (Reviewers)

### Access the Staging App

**URL:** https://terrarisk.arlexperalta.com

### What to Test

1. **Homepage**
   - Map loads correctly
   - Municipalities list appears
   - Tabs switch properly

2. **Workshop Flow**
   - Create groups
   - Assign municipalities
   - Drag & drop works
   - Generate bivariate maps
   - Download PNG files

3. **Performance**
   - Initial load < 3s
   - Map generation < 10s
   - No console errors

### Report Issues

Send to Arlex:
- URL where error occurs
- Screenshot
- Steps to reproduce
- Browser and version

---

## Architecture

```
Internet → DNS → Nginx Proxy Manager → Docker Network
                        ↓
                  [Frontend: 4001] ↔ [Backend: 8002]
```

**Tech Stack:**
- Frontend: Next.js 14 (standalone)
- Backend: FastAPI + Uvicorn
- Container: Docker + Docker Compose
- Proxy: Nginx Proxy Manager
- SSL: Let's Encrypt (auto)

---

## Useful Commands (Server)

```bash
# Deploy from scratch
./deploy.sh start

# Update code and restart
./deploy.sh update

# View logs
./deploy.sh logs

# Check health
./deploy.sh health

# Verify deployment
./verify-deployment.sh
```

---

## Configuration Files

### Docker & Environment

- `docker-compose.prod.yml` - Production config
- `.env.production` - Environment variables
- `.dockerignore` - Build exclusions (root, backend, frontend)

### Scripts

- `deploy.sh` - Automated deploy script
- `verify-deployment.sh` - Post-deploy verification

### Documentation

- All `.md` files in root directory

---

## Troubleshooting

### Issue: Services won't start

```bash
./deploy.sh logs
```

### Issue: 502 Bad Gateway

```bash
docker ps
./deploy.sh restart
```

### Issue: SSL not working

See: `NGINX-PROXY-MANAGER-SETUP.md`

---

## Project Info

| Attribute | Value |
|-----------|-------|
| **Domain** | terrarisk.arlexperalta.com |
| **Server** | Contabo VPS 161.97.95.132 |
| **Repo** | https://github.com/adgch86/saopaulo-biodiversity-health |
| **Branch** | workshop-ui-fixes |
| **Owner** | Dr. Adrian David González |
| **DevOps** | Arlex Peralta |

---

## Next Steps

1. **Deploy** - Follow QUICK-START.md
2. **Verify** - Run verify-deployment.sh
3. **Test** - Adrian and Monti test the app
4. **Monitor** - Setup uptime monitoring (optional)
5. **Backup** - Configure automatic backups (optional)

---

## Support

For questions or issues:
- **DevOps:** Arlex Peralta
- **Project Owner:** Dr. Adrian David González

---

**Last Updated:** 2026-02-10
**Version:** 1.0.0
**Status:** Ready for deployment
