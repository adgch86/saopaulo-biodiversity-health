# Lazy Loading de i18n - Implementación Completa

## Problema Resuelto

**ANTES:** El `layout.tsx` cargaba TODOS los mensajes de i18n (~300 keys × 3 locales) y los serializaba en el HTML inicial de CADA request, aumentando el TTFB a ~670ms.

**AHORA:** Cada página solo carga los namespaces que necesita, reduciendo drásticamente el tamaño del HTML inicial.

## Cambios Implementados

### 1. Root Layout (`src/app/layout.tsx`)

**Modificación:** Solo pasa `common` y `categories` al provider global.

```tsx
const layoutMessages = {
  common: (messages as any).common,
  categories: (messages as any).categories,
};

<NextIntlClientProvider messages={layoutMessages}>
  {children}
</NextIntlClientProvider>
```

### 2. Landing Page

**Archivos:**
- `src/app/page.tsx` (NUEVO - Server Component)
- `src/app/LandingClient.tsx` (RENOMBRADO del anterior page.tsx)

**Namespaces cargados:** `landing`

```tsx
// page.tsx
const pageMessages = {
  landing: (messages as any).landing,
};

return (
  <NextIntlClientProvider messages={pageMessages}>
    <LandingClient />
  </NextIntlClientProvider>
);
```

### 3. Workshop Page

**Archivos:**
- `src/app/workshop/page.tsx` (NUEVO - Server Component)
- `src/app/workshop/WorkshopClient.tsx` (RENOMBRADO del anterior page.tsx)

**Namespaces cargados:**
- `workshop`
- `workshopFlow`
- `layers`
- `purchase`
- `municipality`
- `strategy`
- `layerNames`
- `layerDescriptions`
- `radarChart`
- `bipartiteNetwork`
- `actionNames`
- `actionDescriptions`

### 4. Admin Page

**Archivos:**
- `src/app/admin/page.tsx` (NUEVO - Server Component)
- `src/app/admin/AdminClient.tsx` (RENOMBRADO del anterior page.tsx)

**Namespaces cargados:**
- `admin`
- `landing` (para labels de áreas profesionales)

### 5. Login Page

**Sin cambios** - No usa i18n, todo hardcoded.

## Arquitectura

```
Root Layout (Server)
├── NextIntlClientProvider (common + categories)
│
└── Page (Server Component)
    ├── getMessages() - Carga solo namespaces necesarios
    │
    └── NextIntlClientProvider (namespaces específicos)
        └── ClientComponent
            └── useTranslations('namespace')
```

**Ventajas:**
1. Los providers se anidan y mergen automáticamente
2. Los componentes hijo acceden a AMBOS providers (global + page-specific)
3. Zero cambios en la lógica de negocio
4. Compatible con todas las features de next-intl

## Reducción de Tamaño

### Estimación (PT locale)

| Página | Antes | Ahora | Reducción |
|--------|-------|-------|-----------|
| Landing | ~300 keys | ~50 keys | ~83% |
| Workshop | ~300 keys | ~200 keys | ~33% |
| Admin | ~300 keys | ~60 keys | ~80% |
| Login | ~300 keys | 0 keys | ~100% |

**Nota:** `common` y `categories` (~30 keys) siempre se cargan en el layout global.

## Cómo Probar

### 1. Verificar HTML inicial más pequeño

```bash
curl -s http://localhost:3000 | wc -c
curl -s http://localhost:3000/admin | wc -c
```

Comparar el tamaño del HTML antes y después.

### 2. Verificar TTFB reducido

En Chrome DevTools → Network → Reload:
- Buscar el documento principal
- Ver "Waiting (TTFB)"
- Debería ser ~200-300ms menos que antes

### 3. Verificar funcionalidad

- Landing: Crear/unir grupo, cambiar idioma
- Workshop: Todo el flujo de 5 pasos
- Admin: Ver estadísticas, resetear créditos
- Login: Autenticación

Todo debe funcionar exactamente igual que antes.

## Archivos Modificados

```
✓ src/app/layout.tsx (modificado)
✓ src/app/page.tsx (reescrito como server component)
✓ src/app/LandingClient.tsx (nuevo - código del anterior page.tsx)
✓ src/app/workshop/page.tsx (reescrito como server component)
✓ src/app/workshop/WorkshopClient.tsx (nuevo - código del anterior page.tsx)
✓ src/app/admin/page.tsx (reescrito como server component)
✓ src/app/admin/AdminClient.tsx (nuevo - código del anterior page.tsx)
✓ src/app/login/page.tsx (sin cambios)
```

## Próximos Pasos (Opcional)

1. **Code splitting adicional:** Si `workshop` aún es grande, dividir en sub-namespaces por step
2. **Medición real:** Comparar TTFB en producción con herramientas como Vercel Analytics o Cloudflare Insights
3. **Preload crítico:** Considerar preload de namespaces que se van a usar pronto (ej: workshop desde landing)

## Compatibilidad

- Next.js 14.2.35 ✓
- next-intl 4.8.2 ✓
- App Router ✓
- Server Components ✓
- Client Components ✓
- Nested Providers ✓

---

**Implementado:** 2026-02-12
**Impacto esperado:** Reducción de ~30-50% en TTFB para landing/admin, ~15-20% para workshop
