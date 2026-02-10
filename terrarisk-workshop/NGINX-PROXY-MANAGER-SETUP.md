# Nginx Proxy Manager - Configuración TerraRisk

Guía detallada para configurar el proxy host de TerraRisk Workshop en Nginx Proxy Manager.

---

## Pre-requisitos

- Nginx Proxy Manager corriendo en el VPS Contabo
- Servicios TerraRisk levantados (docker-compose up)
- DNS configurado apuntando a 161.97.95.132

---

## Acceso a Nginx Proxy Manager

**URL:** http://161.97.95.132:81

**Credenciales por defecto:**
- Email: `admin@example.com`
- Password: `changeme`

**IMPORTANTE:** Cambiar password en el primer login.

---

## Paso 1: Crear Proxy Host

1. Click en **"Hosts"** → **"Proxy Hosts"** en el menú lateral
2. Click en **"Add Proxy Host"** (botón azul superior derecho)

---

## Paso 2: Configurar Detalles del Proxy

### Pestaña "Details"

| Campo | Valor |
|-------|-------|
| **Domain Names** | `terrarisk.arlexperalta.com` |
| **Scheme** | `http` |
| **Forward Hostname / IP** | `172.17.0.1` (IP del host Docker) |
| **Forward Port** | `4001` |
| **Cache Assets** | ✓ (opcional, mejora performance) |
| **Block Common Exploits** | ✓ |
| **Websockets Support** | ✓ (importante para Next.js) |

**Nota sobre Forward Hostname:**
- `172.17.0.1` es la IP del host Docker (gateway por defecto)
- Alternativa: usar `host.docker.internal` si NPM está en modo host network
- Si no funciona, probar con la IP privada del VPS (ej: `10.0.0.1`)

**Para verificar la IP correcta:**

```bash
# Desde el VPS
docker network inspect bridge | grep Gateway
# Usar la IP que aparece como Gateway
```

---

## Paso 3: Configurar SSL

### Pestaña "SSL"

| Campo | Valor |
|-------|-------|
| **SSL Certificate** | Dropdown → **"Request a new SSL Certificate"** |
| **Force SSL** | ✓ (redirige HTTP a HTTPS) |
| **HTTP/2 Support** | ✓ |
| **HSTS Enabled** | ✓ |
| **HSTS Subdomains** | ☐ (no aplica) |
| **Email Address for Let's Encrypt** | Tu email real (ej: `arlex@arlexperalta.com`) |
| **I Agree to the Let's Encrypt Terms of Service** | ✓ |

**Resultado esperado:**
- SSL se genera automáticamente en 30-120 segundos
- Certificado válido por 90 días (se renueva automáticamente)

---

## Paso 4: Configuración Avanzada (Opcional)

### Pestaña "Advanced"

Si necesitas headers personalizados, agregar:

```nginx
# Custom headers para Next.js
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_set_header X-Forwarded-Host $host;

# Aumentar timeout para generación de mapas (puede tardar)
proxy_read_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;

# Buffers para respuestas grandes
proxy_buffering on;
proxy_buffer_size 4k;
proxy_buffers 8 4k;
proxy_busy_buffers_size 8k;
```

**Solo agregar si tienes problemas de timeout o headers.**

---

## Paso 5: Guardar y Verificar

1. Click en **"Save"**
2. Esperar 30-120 segundos (generación de SSL)
3. El proxy host debe aparecer en la lista con:
   - Estado: **"Online"** (punto verde)
   - SSL: **"Let's Encrypt"**
   - Dominio: `terrarisk.arlexperalta.com`

---

## Verificación

### Desde terminal (VPS)

```bash
# Test HTTP (debe redirigir a HTTPS)
curl -I http://terrarisk.arlexperalta.com

# Test HTTPS
curl -I https://terrarisk.arlexperalta.com

# Verificar certificado SSL
echo | openssl s_client -servername terrarisk.arlexperalta.com -connect terrarisk.arlexperalta.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Desde navegador

1. Abrir: https://terrarisk.arlexperalta.com
2. Verificar candado verde (SSL válido)
3. Click en el candado → "Certificate is valid"
4. La app debe cargar correctamente

---

## Troubleshooting

### Problema: SSL no se genera

**Síntomas:**
- Error: "Failed to obtain SSL certificate"
- Proxy host aparece pero sin SSL

**Soluciones:**

1. **Verificar DNS propagado:**

```bash
nslookup terrarisk.arlexperalta.com
# Debe resolver a 161.97.95.132
```

2. **Verificar puertos abiertos en firewall:**

```bash
# Verificar puerto 80 (necesario para Let's Encrypt)
sudo ufw status | grep 80

# Verificar puerto 443
sudo ufw status | grep 443

# Si están bloqueados, abrir:
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

3. **Ver logs de Nginx Proxy Manager:**

```bash
docker logs -f nginx-proxy-manager
```

4. **Reiniciar NPM:**

```bash
docker restart nginx-proxy-manager
```

---

### Problema: "502 Bad Gateway"

**Síntomas:**
- HTTPS funciona pero muestra error 502
- Frontend no carga

**Soluciones:**

1. **Verificar que frontend esté corriendo:**

```bash
docker ps | grep terrarisk-frontend
curl http://localhost:4001
```

2. **Verificar la IP de forwarding:**

```bash
# Obtener IP correcta del host
docker network inspect bridge | grep Gateway

# Actualizar "Forward Hostname/IP" en NPM con esa IP
```

3. **Probar con IP privada del servidor:**

En NPM, cambiar Forward Hostname de `172.17.0.1` a la IP privada del VPS (usar `ip addr` para obtenerla).

---

### Problema: "This site can't provide a secure connection"

**Síntomas:**
- Error ERR_SSL_PROTOCOL_ERROR
- Certificado inválido

**Soluciones:**

1. **Regenerar certificado:**
   - En NPM: Edit proxy host → SSL tab
   - Click "Force Reissue Certificate"

2. **Verificar que Force SSL esté activado**

3. **Limpiar caché del navegador**

---

### Problema: API calls fallan desde frontend

**Síntomas:**
- Frontend carga pero no muestra datos
- Console error: "Failed to fetch"

**Causa:**
- Backend API no es accesible desde el navegador (CORS)

**Solución:**

El frontend debe hacer proxy de las requests al backend. Verificar en `next.config.mjs`:

```javascript
async rewrites() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return [
    {
      source: '/api/:path*',
      destination: `${apiUrl}/api/:path*`,
    },
  ];
}
```

Si falta, las requests de `fetch('/api/...')` fallarán.

---

## Configuración Multi-Dominio (Opcional)

Si quieres que la API sea accesible directamente:

1. Crear **segundo proxy host**:
   - Domain: `terrarisk-api.arlexperalta.com`
   - Forward Port: `8002`
   - SSL: Igual que el frontend

2. Configurar DNS para `terrarisk-api`:

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | terrarisk-api | 161.97.95.132 | Auto |

3. Resultado:
   - Frontend: https://terrarisk.arlexperalta.com
   - API directa: https://terrarisk-api.arlexperalta.com/api/health

---

## Mantenimiento

### Renovación SSL

- **Automática:** Let's Encrypt se renueva automáticamente 30 días antes de expirar
- **Manual:** Edit proxy host → SSL tab → "Force Reissue Certificate"

### Ver certificados actuales

En NPM:
1. Click "SSL Certificates" en menú lateral
2. Buscar `terrarisk.arlexperalta.com`
3. Ver fecha de expiración

### Logs de acceso

```bash
# Logs de Nginx Proxy Manager
docker logs -f nginx-proxy-manager

# Logs de acceso (dentro del contenedor)
docker exec -it nginx-proxy-manager tail -f /data/logs/proxy-host-*.log
```

---

## Checklist de Configuración

- [ ] Proxy host creado con dominio correcto
- [ ] Forward Hostname/IP apunta a `172.17.0.1:4001`
- [ ] Websockets Support activado
- [ ] Block Common Exploits activado
- [ ] SSL generado correctamente (Let's Encrypt)
- [ ] Force SSL activado
- [ ] HTTP/2 Support activado
- [ ] HSTS Enabled activado
- [ ] Proxy host en estado "Online"
- [ ] HTTPS accesible desde navegador
- [ ] Certificado SSL válido (candado verde)
- [ ] App carga correctamente sin errores 502

**Configuración completa cuando todos los items están chequeados.**
