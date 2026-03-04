# Sentry Setup - TerraRisk Workshop

Configuración de monitoreo de errores con Sentry para frontend (Next.js) y backend (FastAPI).

## Estado Actual

- ✅ Configuración de Sentry instalada en frontend y backend
- ✅ Sentry se activa SOLO si `SENTRY_DSN` tiene valor (graceful degradation)
- ✅ Sample rates bajos (0.2) para no saturar cuenta free de Sentry
- ❌ Variables de entorno pendientes de configurar

## Próximos Pasos

### 1. Crear Proyecto en Sentry

1. Ve a https://sentry.io (o crea cuenta si no tienes)
2. Crea nuevo proyecto:
   - **Platform:** Next.js (para frontend)
   - **Platform:** Python/FastAPI (para backend)
   - **Alert frequency:** Default
3. Copia el **DSN** de cada proyecto

### 2. Configurar Frontend

En `frontend/.env.local` (crear si no existe):

```bash
# Sentry - Frontend
NEXT_PUBLIC_SENTRY_DSN=https://xxxxx@o123456.ingest.us.sentry.io/789012
SENTRY_ORG=tu-organizacion
SENTRY_PROJECT=terrarisk-frontend
```

### 3. Configurar Backend

En `backend/.env`:

```bash
# Sentry - Backend
SENTRY_DSN=https://xxxxx@o123456.ingest.us.sentry.io/789013
ENVIRONMENT=production
```

### 4. Instalar Dependencias

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### 5. Verificar Funcionamiento

#### Frontend

```bash
cd frontend
npm run dev
```

Visita http://localhost:3000 y fuerza un error para verificar que Sentry lo captura.

#### Backend

```bash
cd backend
uvicorn main:app --reload
```

Endpoint de salud: http://localhost:8000/api/health

## Configuración Técnica

### Frontend (Next.js)

- **Config files:**
  - `sentry.client.config.ts` - Cliente (navegador)
  - `sentry.server.config.ts` - Server-side rendering
  - `sentry.edge.config.ts` - Edge runtime
  - `src/app/global-error.tsx` - Error boundary global

- **Sample rates:**
  - `tracesSampleRate: 0.2` - 20% de transacciones
  - `replaysOnErrorSampleRate: 1.0` - 100% de replays en errores
  - `replaysSessionSampleRate: 0` - 0% de replays de sesiones normales

- **Source maps:** Deshabilitados (`disableSourceMapUpload: true`) para no exponer código

### Backend (FastAPI)

- **Init:** En `main.py` ANTES de crear la app FastAPI
- **Sample rates:**
  - `traces_sample_rate: 0.2` - 20% de transacciones
  - `profiles_sample_rate: 0.1` - 10% de perfiles de performance
- **Environment:** Configurable via `ENVIRONMENT` env var

## Comportamiento

### Con Sentry Habilitado (DSN configurado)

- ✅ Errores enviados a Sentry automáticamente
- ✅ Performance tracking (20% de requests)
- ✅ Session replays en errores (frontend)
- ✅ Contexto completo (user, request, stack trace)

### Sin Sentry (DSN vacío o no configurado)

- ✅ App funciona normalmente
- ✅ Logs locales siguen funcionando
- ✅ No se rompe nada
- ✅ Zero overhead

## Dashboards Útiles

Una vez configurado:

- **Issues:** https://sentry.io/organizations/[org]/issues/
- **Performance:** https://sentry.io/organizations/[org]/performance/
- **Releases:** https://sentry.io/organizations/[org]/releases/

## Rate Limiting

Para no saturar cuota free de Sentry:

| Métrica | Valor | Razón |
|---------|-------|-------|
| Traces Sample Rate | 0.2 | Solo 20% de requests |
| Replays (error) | 1.0 | Capturar TODO error |
| Replays (session) | 0.0 | Caro, solo errores |
| Profiles Sample Rate | 0.1 | Performance profiling ligero |

## Troubleshooting

### Frontend no envía errores

1. Verificar que `NEXT_PUBLIC_SENTRY_DSN` esté en `.env.local`
2. Verificar que el DSN sea correcto (debe empezar con `https://`)
3. Reiniciar `npm run dev`
4. Revisar consola del navegador (debe decir "Sentry initialized")

### Backend no envía errores

1. Verificar que `SENTRY_DSN` esté en `.env`
2. Verificar que `sentry-sdk[fastapi]` esté instalado
3. Reiniciar servidor
4. Forzar un error y revisar Sentry dashboard

### Source maps no suben

- Esto es INTENCIONAL. `disableSourceMapUpload: true` evita exponer código fuente.
- Si quieres habilitar, cambia a `false` y configura `SENTRY_AUTH_TOKEN`.

## Seguridad

- ✅ `.env` y `.env.local` están en `.gitignore`
- ✅ DSNs son públicos (solo envían datos, no los leen)
- ✅ Source maps NO se suben (código protegido)
- ✅ API keys NO se capturan (filtros automáticos de Sentry)

## Recursos

- [Sentry Next.js Docs](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Sentry FastAPI Docs](https://docs.sentry.io/platforms/python/integrations/fastapi/)
- [Best Practices](https://docs.sentry.io/product/best-practices/)
